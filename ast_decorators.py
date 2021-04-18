import ast 
import inspect



# A decorator which loads and modifies a functions AST instead of working with it as a python object. 
#	They're super janky and can't be composed in the usual way, because they have no source for the next level to read.
class AstDecorator:
	endpoints = set()
	
	def __init__(self, ast_func, post_wrap = lambda x: x):
		self.ast_func = ast_func
		self.post_wrap = post_wrap

	def __call__(self, f):
		locals_capture = "True"

		tree = ast.parse(fixindentation(inspect.getsource(f)))

		# Don't run any decorators right now
		tree.body[0].decorator_list = []

		# apply the ast_func
		tree = self.ast_func(tree)

		# change the def node to define a function called "_"
		tree.body[0].name = "_"

		tree = ast.fix_missing_locations(tree)

		code = compile(tree, "<string>", "exec")
		exec(code)

		# get the newly created function from locals
		new_f = locals()["_"]

		# allow this function to act as the top level for the local vars to bubble up to
		AstDecorator.endpoints.add(self.__call__.__code__)

		# apply the post_wrap function
		# pre_vals = locals()
		new_f = self.post_wrap(new_f)

		# allow the wrapped function to act as the top level for the local vars to bubble up to
		if new_f is not None:
			AstDecorator.endpoints.add(new_f.__code__)

		return new_f

	# run from left to right for some reason
	def __mul__(self, other):
		def ast_func(tree):
			return other.ast_func(self.ast_func(tree))
		def post_wrap(f):
			f = other.post_wrap(self.post_wrap(f))
			return f

		return AstDecorator(ast_func, post_wrap)


# Has to be the last AstDecorator applied
def immediate():
	def ast_func(tree):
		return tree
	def post_wrap(f):
		return f()
	return AstDecorator(ast_func, post_wrap)
immediate = immediate()#eww js style why did I do this

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
			# if the indentation is fine, just return the input
			if indentation == 0:
				return source
		result += line[indentation:] + "\n"

	return result

def on(target):
	import ast
	import inspect
	from copy import deepcopy

	class Attributer(ast.NodeTransformer):

		def visit_Expr(self, node: ast.Expr):

			if not isinstance(node.value, ast.Call) or not isinstance(node.value.func, ast.Name):
				return node

			#we have a raw function call like "setup(1000, 1000)"
			func = node.value.func

			if not hasattr(target, func.id):
				return node

			# make a new function that is an attribute of target instead of a raw name
			new_func = ast.Attribute(ast.Name(target.__name__, ast.Load()), func.id, ast.Load())

			# copy the node
			result = deepcopy(node)
			# replace the function call with the new one, fix the line_no 
			result.value.func = ast.fix_missing_locations(ast.copy_location(new_func, func))

			return ast.copy_location(result, node)

	def ast_func(tree):
		return Attributer().visit(tree)

	def post_func(f):
		f.__globals__[target.__name__] = target
		return f

	return AstDecorator(ast_func, post_func)


def on_block(target):

	return no_locals * on(target) * immediate

	def wrap(f):

		decorators = no_locals() * on(target)
		g = decorators(f)
		g()

		def oops_janky_hack(*args, **kwargs):
			raise NotImplementedError("Attempted to call an @on_block.  Use @on if you want to actually define a function.  ")
		return oops_janky_hack

	return wrap

def no_locals():
	import ast
	import inspect
	from copy import deepcopy



	def globalify():
		vals = locals()

		from inspect import currentframe

		frame = currentframe()

		# search for the function noted as the upper endpoint
		x = frame
		while x is not None:
			if x.f_code in AstDecorator.endpoints:
				break
			
			x = x.f_back
		else:
			raise SyntaxError("Couldn't find the upper endpoint for locals to bubble up to")

		try:
			x.f_back.f_locals.update(vals)
		finally:
			del frame
			del x

	def ast_func(tree):
		hook_tree = ast.parse(fixindentation(inspect.getsource(globalify)))

		# try:
		#	f()
		# finally:
		#	hook()
		try_wrap = ast.Try(body=deepcopy(tree.body[0].body) , handlers=[], orelse=[], finalbody=deepcopy(hook_tree.body[0].body))

		tree.body[0].body = [try_wrap]
		return tree

	def post_wrap(f):
		f._no_locals = True

		return f

	return AstDecorator(ast_func, post_wrap)
no_locals = no_locals()