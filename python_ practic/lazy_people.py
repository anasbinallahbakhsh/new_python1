from turtle import *
import colorsys

setup(900,900)
bgcolor("black")
title("Python Spiral Art")

speed(0)
tracer(0)
hideturtle()

pensize(2)

h = 0

for i in range(360):

    c = colorsys.hsv_to_rgb(h,1,1)
    pencolor(c)

    forward(i*2)

    right(59)

    circle(120,90)

    left(120)

    circle(120,90)

    right(61)

    forward(30)

    backward(30)

    h += 0.004

    update()

penup()
goto(0,0)

for i in range(150):

    c = colorsys.hsv_to_rgb(h,1,1)
    pencolor(c)

    pendown()

    circle(i*1.2)

    left(5)

    h += 0.01

    update()

penup()
goto(0,-200)

write(
    "Created with Python ❤️",
    align="center",
    font=("Arial",18,"bold")
)

done()








