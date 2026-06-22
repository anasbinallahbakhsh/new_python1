import turtle
import math
import random
import colorsys
def main():
    screen = turtle.Screen()
    screen.setup(width=800, height=800)
    screen.bgcolor("#CD3131")
    screen.title("Nebula Heart")
    screen.tracer(300)
    
    swarm_size = 300
    particles = []
    
    for _ in range(swarm_size):
        p = turtle.Turtle(shape="circle")
        p.speed(0)
        p.penup() 
        p.shapesize(0.2)
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(50, 300)
        p.goto(dist * math.cos(angle), dist * math.sin(angle))
        particles.append(p)
    
    def heart_x(t):
        return 16 * (math.sin(t) ** 3)
    
    def heart_y(t):
        return 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
    
    for frame in range(500):
        for i, p in enumerate(particles):
            x, y = p.xcor(), p.ycor()
            
            t = (i / swarm_size) * 2 * math.pi
            target_x = heart_x(t) * 15
            target_y = heart_y(t) * 15
            
            dx = target_x - x
            dy = target_y - y
            
            x += dx * 0.05
            y += dy * 0.05
            
            p.goto(x, y)
            
            hue = (frame / 500 + i / swarm_size) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            p.color(r, g, b)
        
        screen.update()
    
    turtle.done()

main()
