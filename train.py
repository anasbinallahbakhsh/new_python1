import turtle
import random

screen = turtle.Screen()
screen.setup(900, 600)
screen.bgcolor("#87CEEB")
screen.tracer(0)

t = turtle.Turtle()
t.hideturtle()
t.speed(0)
t.penup()

train_x = -600
smoke = []
clouds = [(random.randint(-400, 400), random.randint(150, 220)) for _ in range(4)]


def rect(x, y, w, h, color):
    t.goto(x, y)
    t.color(color)
    t.begin_fill()
    for _ in range(2):
        t.forward(w)
        t.left(90)
        t.forward(h)
        t.left(90)
    t.end_fill()


def circle(x, y, r, color):
    t.goto(x, y - r)
    t.color(color)
    t.begin_fill()
    t.circle(r)
    t.end_fill()


def draw_scene(x):
    # sky
    rect(-450, 50, 900, 250, "#87CEEB")

    # sun
    circle(320, 220, 35, "#FFD54F")

    # clouds
    for cx, cy in clouds:
        for dx, dy, r in [(0, 0, 20), (18, 5, 15), (-18, 5, 15)]:
            circle(cx + dx, cy + dy, r, "white")

    # ground (grass)
    rect(-450, -150, 900, 60, "#4CAF50")

    # railway bed (gravel)
    rect(-450, -160, 900, 15, "#6d4c41")

    # rail tracks (two lines)
    t.pensize(3)
    t.color("#333")
    t.goto(-450, -152)
    t.pendown()
    t.goto(450, -152)
    t.penup()
    t.goto(-450, -158)
    t.pendown()
    t.goto(450, -158)
    t.penup()
    t.pensize(1)

    # sleepers (wooden planks under track)
    for sx in range(-440, 450, 30):
        rect(sx, -160, 8, 10, "#5d4037")

    # trees
    for tx in range(-430, 460, 110):
        rect(tx - 4, -110, 8, 35, "#6d4c41")
        circle(tx, -60, 32, "#2e7d32")
        circle(tx - 15, -75, 22, "#388e3c")
        circle(tx + 15, -75, 22, "#388e3c")

    # ---- TRAIN ----
    # shadow under train
    circle(x + 100, -125, 105, "#cccccc")

    # main body
    rect(x, -90, 210, 75, "#e53935")
    rect(x, -95, 210, 8, "#b71c1c")  # bottom shade

    # cabin (raised back section)
    rect(x + 150, -35, 55, 45, "#c62828")
    rect(x + 150, -35, 55, 8, "#fff59d")  # roof stripe

    # front nose
    rect(x - 15, -75, 15, 55, "#c62828")

    # windows
    for i in range(3):
        rect(x + 20 + i * 55, -45, 35, 28, "#e1f5fe")
        rect(x + 20 + i * 55, -45, 35, 4, "#4fc3c7")

    # cabin window
    rect(x + 160, -20, 30, 22, "#e1f5fe")

    # stripe on body
    rect(x, -70, 210, 6, "#ffee58")

    # wheels with rim detail
    for i in range(4):
        wx = x + 25 + i * 50
        circle(wx, -108, 16, "#212121")
        circle(wx, -108, 6, "#757575")

    # chimney
    rect(x - 5, -35, 12, 25, "#424242")


def draw_smoke():
    global smoke
    smoke.append([train_x + 1, -20, 4, 255])

    for p in smoke:
        r = max(1, int(p[2]))
        t.penup()
        circle(p[0], p[1], r, "gray")
        p[0] += random.uniform(-0.3, 0.6)
        p[1] += 2
        p[2] += 0.35
        p[3] -= 6

    smoke[:] = [p for p in smoke if p[3] > 0]


def move_train():
    global train_x
    train_x += 4
    if train_x > 550:
        train_x = -600
        smoke.clear()

    t.clear()
    draw_scene(train_x)
    draw_smoke()
    screen.update()
    screen.ontimer(move_train, 30)


move_train()
screen.mainloop()