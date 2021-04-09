# from turtle import *
import turtle



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


#probably only works on top level function definitions
def on(prefix):
	def wrap(f):
		import inspect

		# name of the function
		#	we could pull this from the code by searching for the 'def' line
		fname = f.__name__


		py_code_lines = inspect.getsource(f).split("\n")
		py_code = ""
		first = True
		for line in py_code_lines:
			#ignore empty lines and decorators
			if line.isspace() or len(line) == 0 or line[0] == "@":
				continue
			#don't prefix the def line
			if first:	
				py_code = line + '\n'
				first = False
				continue
			py_code += insert_after_whitespace(line, prefix) + '\n'

		#execute the modified def code
		exec(py_code)

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


@on("turtle.")
def a():
	setup(1000, 1000)
	forward(100)
	hideturtle()
