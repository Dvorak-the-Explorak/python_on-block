from on_block import on



# from turtle import *
import turtle
turtle.setup()

@on(turtle)
def a():
	# print(xcor(), ycor())
	for i in range(4):
		forward(100)
		left(90)
	hideturtle()

turtle.done()