from ast_decorators import on_block, no_locals

# from turtle import *
import turtle
turtle.setup()

def close_turtle_window(*args):
	turtle.getscreen().getcanvas()._rootwindow.quit()


@on_block(turtle)
def _():
	localvar = 100
	print(xcor(), ycor())
	speed("fastest")
	print("This won't be converted to 'turtle.print'")
	for i in range(4):
		pass
		forward(100)
		left(90)
	hideturtle()
try:
	print(f"localvar is: {localvar}")
except:
	print("localvar not defined outside on_block")

del _
del localvar

def double():
	double_nonlocal = "hello"
	def nested():
		
		nonlocal_variable = "hello"
		@on_block(turtle)
		def _():
			localvar = 100
			print(nonlocal_variable)
			speed("fastest")
			print("This won't be converted to 'turtle.print'")
			for i in range(4):
				pass
				forward(100)
				left(90)
			hideturtle()
			close_turtle_window()
		try:
			print(localvar)
		except NameError as e:
			print("localvar not defined outside on_block")

	try:
		print(localvar)
	except NameError as e:
		print("localvar not defined 2 levels out of on_block")

	return nested
		
double()()




@no_locals
def f():
	print("Defining x")
	x = 10
f()
try:
	print(x)
except:
	print("x not defined after @no_locals function called")




turtle.done()