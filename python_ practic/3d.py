import turtle
import math
import random

screen = turtle.Screen()
screen.setup(width=800, height=800)
screen.bgcolor("#0b0f19")
screen.title("Mandala Art")
screen.tracer(2)

artist = turtle.Turtle()
artist.hideturtle()
artist.speed(0)
artist.pensize(1.5)

colors = [
    "#ff2a6d", "#05d9e8", "#ff007f", "#39ff14",
    "#ffe600", "#9d00ff", "#00ffcc", "#ff5500"
]

def draw_mandala():
    num_petals = 12
    layers = 8

    for layer in range(1, layers + 1):
        radius = layer * 25
        color_choice = colors[(layer - 1) % len(colors)]
        artist.pencolor(color_choice)

        for i in range(num_petals):
            angle = (i * 360 / num_petals)
            rad = math.radians(angle)
            x = radius * math.cos(rad)
            y = radius * math.sin(rad)

            artist.penup()
            artist.goto(x, y)
            artist.pendown()
            artist.setheading(angle)

            petal_size = radius * 0.35 + random.randint(6, 16)

            for _ in range(2):
                artist.circle(petal_size, 60)
                artist.left(120)

            artist.penup()
            artist.goto(x, y)
            artist.dot(max(4, int(layer * 1.8)), random.choice(colors))

    artist.penup()
    artist.goto(0, -12)
    artist.pendown()
    artist.pencolor("white")
    artist.dot(28, random.choice(colors))

draw_mandala()
screen.update()
turtle.done()