import turtle
import colorsys
import math

def draw_vortex_effect():
    screen = turtle.Screen()
    screen.bgcolor("black")
    screen.title("Chromospheric")

    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    screen.tracer(2, 0)
    
    hue = 0.0
    iterations = 400
    magic_angle = 121

    try:
        for i in range(iterations):
            color = colorsys.hsv_to_rgb(hue, 0.9, 1)
            t.color(color)
            
            size = i * 2
            t.forward(size)
            t.right(magic_angle)
            
            hue += 1.0 / iterations
            
            if i % 10 == 0:
                screen.update()

    except turtle.Terminator:
        pass

    screen.update()
    screen.mainloop()

draw_vortex_effect()