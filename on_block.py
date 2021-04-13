



def just_say_yes(*args, **kwargs):
	print("Yes")

def describe(name, x):
	print("=============")
	print(name)
	print(type(x))
	print(x)
	print(dir(x))
	print("=============\n")

def insert_after_whitespace(string, add):
	if len(string) == 0:
		return add

	i = 0
	while i < len(string) and string[i].isspace():
		i += 1
	return string[:i] + add + string[i:]

def interact_tree(src):
	import ast
	from itertools import dropwhile

	tree = ast.parse(src.lstrip())

	import code
	variables = {**globals(), **locals()}
	shell = code.InteractiveConsole(variables)
	shell.interact()



#probably only works on top level function definitions
def on(target):
	import ast
	import turtle
	import inspect 
	from copy import deepcopy

	this_decorator = fname = inspect.currentframe().f_code.co_name

	class Attributer(ast.NodeTransformer):

		def visit_Expr(self, node: ast.Expr):

			if not isinstance(node.value, ast.Call) or not isinstance(node.value.func, ast.Name):
				return node

			#we have a raw function call like "setup(1000, 1000)"
			func = node.value.func

			# ignore calls that aren't attributes of target
			if not eval(f"hasattr({target}, '{func.id}')"):
				return node

			# make a new function that is an attribute of turtle instead of a raw name
			new_func = ast.Attribute(ast.Name(target, ast.Load()), func.id, ast.Load())

			# copy the node
			result = deepcopy(node)
			# replace the function call with the new one, fix the line_no 
			result.value.func = ast.fix_missing_locations(ast.copy_location(new_func, func))

			return ast.copy_location(result, node)


	def wrap(f):
		# name of the function
		#	we could pull this from the code by searching for the 'def' line
		fname = f.__name__


		py_code_lines = inspect.getsource(f).split("\n")
		py_code = ""

		att = Attributer()

		tree = ast.parse(inspect.getsource(f), '', 'exec')
		#remove this decorator from the decorator list
		decorators = tree.body[0].decorator_list
		for dec in decorators:
			if dec.func.id == this_decorator:
				decorators.remove(dec)
		

		#replace raw function calls with attributes
		tree = att.visit(tree)
		code = compile(tree, "<string>", "exec")
		exec(code)

		#get the newly created function from locals
		new_f = locals()[fname]

		new_f()


		def oops_janky_hack(*args, **kwargs):
			raise NotImplementedError("Sorry, 'on blocks' are a janky hack, you shouldn't call any function decorated to be an on block.  ")
		return oops_janky_hack
	return wrap

def immediate(f):
	def void(*args, **kwargs):
		return None
	f()
	return void


# from turtle import *
import turtle
turtle.setup()

@on("turtle")
def a():
	print("Hello, world")

	for i in range(4):
		forward(100)
		left(90)
	hideturtle()
	
turtle.done()