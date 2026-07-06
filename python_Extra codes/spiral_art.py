import turtle

s = turtle.Screen()
s.bgcolor("purple")

t = turtle.Turtle()      # Turtle object create kiya
turtle.tracer(4.0)

t.color("yellow")
t.width(1)

for i in range(400):
    t.forward(i * 0.5)
    t.circle(i * 0.9, 90)
    t.left(91)
    t.forward(i * 0.2)
    t.circle(i * 0.1, 90)

t.penup()
t.goto(0, 0)
t.pendown()
tuple.done()
