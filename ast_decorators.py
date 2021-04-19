import ast 
import inspect

#TODO make a preprocessor that lets us use an "on object:" block syntax
#TODO make a recursive version of @on so that function calls are modified too?  sounds even more gross
#TODO on_block disallows "import *" statements because it's still a function definition...
#TODO only change names that don't already exist to turtle.?

# A decorator which loads and modifies a functions AST instead of working with it as a python object. 
#	They're super janky and can't be composed in the usual way, because they have no source for the next level to read.
#TODO in compiling the modified AST, source could be supplied / the ast could be stored to be used for future modifications...
class AstDecorator:
	endpoints = set()

	
	def __init__(self, ast_func, post_wrap = lambda x: x):
		self.ast_func = ast_func
		self.post_wrap = post_wrap

	def __call__(self, f):
		tree = ast.parse(fixindentation(inspect.getsource(f)))

		# Don't run any decorators right now
		tree.body[0].decorator_list = []

		# apply the ast_func
		tree = self.ast_func(tree)

		# change the def node to define a function called "_"
		tree.body[0].name = "_"

		# Get the context of this call as best we can
		#TODO fix the closure issue 
		#		(closure variables are already captured / not by now so we can't grab them from stack frames)
		from inspect import currentframe, getframeinfo
		try:
			frame = currentframe()
			frame = frame.f_back
			allvars = {}
			while frame is not None:
				allvars.update(frame.f_locals)
				frame = frame.f_back
		finally:
			del frame

		# Fix the line numbers required to compile the ast
		tree = ast.fix_missing_locations(tree)

		# Compile the ast into a code object and execute
		code = compile(tree, "<string>", "exec")

		exec(code)

		# get the newly created function from locals
		new_f = locals()["_"]

		# Add the context of the code that called this to the context of the function
		#TODO should this only be for no_locals? 
		#		no because we're moving the function definition elsewhere and have to cover our tracks, right?
		new_f.__globals__.update(allvars)


		# allow this function to act as the top level for the local vars to bubble up to
		#	- must be after the scope modification (I assume the __code__ object changes)
		AstDecorator.endpoints.add(self.__call__.__code__)

		# apply the post_wrap function
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

# Has to be the last AstDecorator applied
def immediate():
	def ast_func(tree):
		return tree
	def post_wrap(f):
		return f()
	return AstDecorator(ast_func, post_wrap)
immediate = immediate()#eww js style why did I do this

def on(target):
	import ast
	import inspect
	from copy import deepcopy

	class Attributer(ast.NodeTransformer):
		def visit_Name(self, node: ast.Name):

			# if the name isn't an attribute of the target, we can't replace it
			if not hasattr(target, node.id):
				return node

			# make a new node that is an attribute of target instead of a raw name
			result = ast.Attribute(ast.Name(target.__name__, ast.Load()), node.id, node.ctx)

			return ast.copy_location(result, node)

	def ast_func(tree):
		return Attributer().visit(tree)

	def post_func(f):
		#TODO should we put the target in locals/args instead of globals?
		#		Probably no for same reason as the scoping fix
		f.__globals__[target.__name__] = target
		return f

	return AstDecorator(ast_func, post_func)


def on_block(target):
	# Tries to create a code block by pushing locally defined variables out of the function when it's done,
	#	and calling the function immediately

	return no_locals * on(target) * immediate

def no_locals():
	import ast
	import inspect
	from copy import deepcopy



	def globalify():
		vals = locals()

		from inspect import currentframe

		# search for the function noted as the upper endpoint
		x = currentframe()

		try:
			while x is not None:
				if x.f_code in AstDecorator.endpoints:
					break
				
				x = x.f_back
			else:
				raise SyntaxError("Couldn't find the upper endpoint for locals to bubble up to")

			# Adding to the function's globals because the locals has weird issues when you try to update it
			#	This won't send the vals into globals, just the function's view of the globals (it seems)
			#TODO verify that using f_globals doesn't break anything
			x.f_back.f_globals.update(vals)
		finally:
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

if __name__ == '__main__':
	import example