# python_on-block
Silly jank project.  

The aim was to create a new control block which would convert function calls into method calls:

on turtle:
  pendown()
  for i in range(4):
    forward(100)
    left(90)
    
would act like:

turtle.pendown()
for i in range(4):
  turtle.forward(100)
  turtle.left(90)

I wanted a block like this for using assessment code written with "from turtle import *" in my own code written with "import turtle".



The @on_block(target) decorator is the attempt at creating this control block.  
  It converts any function call statements to calls to methods in target (whenever target has a method with the same name).  
  It also calls the function in an attempt to emulate a control block.  The function cannot be called in this version.  

The @on(target) decorator can be used as a regular decorator.  

