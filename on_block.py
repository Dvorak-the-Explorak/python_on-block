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



def on(prefix):
	def wrap(f):
		import inspect
		def result(*args, **kwargs):
			code = f.__code__
			fname = f.__name__
			filename = code.co_filename
			lineno = code.co_firstlineno
			linemap = code.co_lnotab


			py_code_lines = inspect.getsource(f).split("\n")
			py_code = ""
			first = True
			for line in py_code_lines:
				#ignore empty lines and decorators
				if line.isspace() or len(line) == 0 or line[0] == "@":
					continue
				#don't prefix the def line
				if first:	
					print("FIRST:", line)
					py_code = line + '\n'
					first = False
					continue
				py_code += insert_after_whitespace(line, prefix) + '\n'

			#execute the modified def code
			exec(py_code)

			#get the newly created function from locals
			new_f = locals()[fname]

			return new_f(*args, **kwargs)
		return result
	return wrap

def immediate(f):
	def void(*args, **kwargs):
		return None
	f()
	return void

@on("turtle.")
def hello_world():
	print("Hello world")


@on("turtle.")
def global_turtle_code():
	setup(1000, 1000)
	forward(100)
	hideturtle()
	done()


global_turtle_code()