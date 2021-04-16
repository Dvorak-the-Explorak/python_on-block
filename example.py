from on_block import on_block

# from turtle import *
import turtle
turtle.setup()

@on_block(turtle)
def _():
	# print(xcor(), ycor())
	for i in range(4):
		forward(100)
		left(90)
	hideturtle()

turtle.done()