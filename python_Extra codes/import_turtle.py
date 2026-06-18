import turtle
import math
import colorsys

screen = turtle.Screen()
screen.bgcolor("black")
screen.title("ULTRA FRACTAL EXPLOSION")
screen.tracer(0, 0)
t = turtle.Turtle()
t.speed(0)
t.width(1)

hue = 0
base_angle = 90

def draw_fractal(x, y, angle, depth, length):
    global hue

    if depth == 0:
        return
    t.penup()
    t.goto(x, y)
    t.setheading(angle)
    t.pendown()
    color = colorsys.hsv_to_rgb(hue % 1, 1, 1)
    t.pencolor(color)
    hue += 0.002
    t.forward(length)
    
    new_x, new_y = t.position()
    
    draw_fractal(new_x, new_y, angle + 30, depth - 1, length * 0.7)
    draw_fractal(new_x, new_y, angle - 30, depth - 1, length * 0.7)

def animate():
    global base_angle
    t.clear()
    draw_fractal(0, -100, base_angle, 10, 100)
    screen.update()
    base_angle += 2          # thori si rotation har baar, taake har tree alag lage
    screen.ontimer(animate, 80)   # 80ms baad dobara chalega -> infinite loop

animate()
screen.mainloop()