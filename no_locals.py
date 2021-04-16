def fixindentation(source):
	# unindents blocks of code in case on block is used nested within another block
	lines = source.split('\n')

	indentation = None
	result = ''
	for line in lines:
		if line.isspace():
			continue
		if indentation is None:
			indentation = len(line) - len(line.lstrip())
		result += line[indentation:] + "\n"

	return result

def concatenate_bodies(f, g):
	if g.__code__.co_argcount + g.__code__.co_kwonlyargcount > 0:
		raise ValueError("Second function must take no arguments")

	import ast
	from inspect import getsource

	f_tree = ast.parse(fixindentation(getsource(f)))
	g_tree = ast.parse(fixindentation(getsource(g)))

	f_tree.body[0].body += g_tree.body[0].body

	# change the def node to define a function called "_"
	f_tree.body[0].name = "_"

	tree = ast.fix_missing_locations(f_tree)

	code = compile(tree, "<string>", "exec")
	exec(code)

	#get the newly created function from locals
	new_f = locals()["_"]

	return new_f




def end_hook(hook):
	if hook.__code__.co_argcount + hook.__code__.co_kwonlyargcount > 0:
		raise ValueError("Hook function must take no arguments")

	import ast
	import inspect
	from copy import deepcopy

	#TODO this assumes the decorator is exactly this function (so can't construct new decorators from this)
	this_decorator = inspect.currentframe().f_code.co_name

	def wrap(f):
		f_tree = ast.parse(fixindentation(inspect.getsource(f)))
		hook_tree = ast.parse(fixindentation(inspect.getsource(hook)))

		# Don't apply any decorators right now
		f_tree.body[0].decorator_list = []

		# try:
		#	f()
		# finally:
		#	hook()
		try_wrap = ast.Try(body=deepcopy(f_tree.body[0].body) , handlers=[], orelse=[], finalbody=deepcopy(hook_tree.body[0].body))


		f_tree.body[0].body = [try_wrap]

		# change the def node to define a function called "_"
		f_tree.body[0].name = "_"

		tree = ast.fix_missing_locations(f_tree)
		# print("HELLO")
		# print(ast.unparse(tree))

		code = compile(tree, "<string>", "exec")
		exec(code)

		#get the newly created function from locals
		new_f = locals()["_"]

		return new_f


	return wrap




def no_locals(f):
	'''Decorator only.  Must be the first decorator applied (closest to def line)'''
	if hasattr(f, "_no_locals") and f._no_locals:
		return f

	import ast
	import inspect
	from copy import deepcopy

	def fixindentation(source):
		# unindents blocks of code in case on block is used nested within another block
		lines = source.split('\n')

		indentation = None
		result = ''
		for line in lines:
			if line.isspace():
				continue
			if indentation is None:
				indentation = len(line) - len(line.lstrip())
			result += line[indentation:] + "\n"

		return result

	try:
		f_source = inspect.getsource(f)
	except OSError:
		print(f"Warning: couldn't apply @no_locals to {f}, source couldn't be found")
		# If we couldn't get the source, we may be applying the decorator for the second time.
		return f

	f_tree = ast.parse(fixindentation(f_source))
	hook_tree = ast.parse(fixindentation(inspect.getsource(globalify)))


	# Don't want any of the decorators to be applied here.  
	# TODO could we force this to be the first decorator?
	#		- somehow run this on the raw function and reapply any earlier decorators...
	f_tree.body[0].decorator_list = []

	# try:
	#	f()
	# finally:
	#	hook()
	try_wrap = ast.Try(body=deepcopy(f_tree.body[0].body) , handlers=[], orelse=[], finalbody=deepcopy(hook_tree.body[0].body))

	f_tree.body[0].body = [try_wrap]

	# change the def node to define a function called "_"
	f_tree.body[0].name = "_"

	tree = ast.fix_missing_locations(f_tree)

	code = compile(tree, "<string>", "exec")
	exec(code)

	#get the newly created function from locals
	new_f = locals()["_"]

	new_f._no_locals = True

	return new_f


def add_end_hook(f, hook):
	return end_hook(hook)(f)


def globalify():
	import inspect
	
	frame = inspect.currentframe()
	try:
		frame.f_back.f_locals.update(locals())
	finally:
		del frame

def twice(f):
	def result(*a, **kw):
		f(*a, **kw)
		f(*a, **kw)
	return result


#TODO jank decorators interact badly with other decorators
if __name__ == "__main__":
	@twice
	@no_locals
	def f():
		print("f")
		x = 10

	try:
		print(x)
	except:
		print("x is not defined")


	f()

	try:
		print(x)
	except:
		print("x is not defined")
