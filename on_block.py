#TODO Add a preprocessing step that looks for "on ___:" blocks instead of using decorators
#TODO functions defined within the @on function definition don't make it out to global scope

def just_say_yes(*args, **kwargs):
	print("Yes")

def describe(name, x):
	print("=============")
	print(name)
	print(type(x))
	print(x)
	print(dir(x))
	print("=============\n")


def interact_tree(src):
	import ast
	from itertools import dropwhile

	tree = ast.parse(src.lstrip())

	import code
	variables = {**globals(), **locals()}
	shell = code.InteractiveConsole(variables)
	shell.interact()


def on(target):
	import ast
	import inspect 
	from copy import deepcopy

	this_decorator = inspect.currentframe().f_code.co_name

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


	def wrap(f):

		att = Attributer()

		tree = ast.parse(fixindentation(inspect.getsource(f)))

		# Don't run any decorators right now
		tree.body[0].decorator_list = []

		# replace raw function calls with attributes
		tree = att.visit(tree)
		code = compile(tree, "<string>", "exec")
		exec(code)

		#get the newly created function from locals
		new_f = locals()[f.__name__]


		# TODO should we add this to closure or something instead
		# add the target to the new function's globals
		#	othewise target may not be defined when this decorator imported into a different module / used in a different scope
		new_f.__globals__[target.__name__] = target
		# We'd really like to give new_f the exact same context - globals and nonlocals etc - as f
		# 		EG new_f.__globals__ = f.__globals__
		#	but if for example turtle is defined in an enclosing function, and turtle is not used in f (before this decorator),
		#	then turtle will not be pulled into the closure, and maybe can't be found from our reference to f...
		new_f()


		def oops_janky_hack(*args, **kwargs):
			raise NotImplementedError("Sorry, 'on blocks' are a janky hack, you shouldn't call any function decorated to be an on block.  ")
		return oops_janky_hack
	return wrap

if __name__ == "__main__":
	def testtt():
		# from turtle import *
		import turtle
		turtle.setup()

		@on(turtle)
		def _():
			print("This won't be turned into turtle.print")
			forward(10)
			def square():
				for i in range(4):
					forward(100)
					left(90)
				hideturtle()
			square()

		turtle.done()
	testtt()