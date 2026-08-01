import pygame, random, sys

pygame.init()
WIDTH, HEIGHT = 600, 400
CELL = 20
FPS = 4

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

BLACK=(0,0,0); GREEN=(0,220,0); RED=(220,40,40); WHITE=(255,255,255)
font=pygame.font.SysFont(None,30)

snake=[(WIDTH//2, HEIGHT//2)]
direction=(1,0)
next_direction=direction

def new_food():
    while True:
        f=(random.randrange(0,WIDTH,CELL), random.randrange(0,HEIGHT,CELL))
        if f not in snake:
            return f

food=new_food()
score=0

running=True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_LEFT and direction!=(1,0):
                next_direction=(-1,0)
            elif event.key==pygame.K_RIGHT and direction!=(-1,0):
                next_direction=(1,0)
            elif event.key==pygame.K_UP and direction!=(0,1):
                next_direction=(0,-1)
            elif event.key==pygame.K_DOWN and direction!=(0,-1):
                next_direction=(0,1)

    direction=next_direction
    hx,hy=snake[-1]
    head=(hx+direction[0]*CELL, hy+direction[1]*CELL)

    if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT or head in snake:
        break

    snake.append(head)

    if head==food:
        score+=1
        food=new_food()
    else:
        snake.pop(0)

    screen.fill(BLACK)
    pygame.draw.rect(screen,RED,(*food,CELL,CELL))
    for x,y in snake:
        pygame.draw.rect(screen,GREEN,(x,y,CELL,CELL))
    screen.blit(font.render(f"Score: {score}",True,WHITE),(10,10))
    pygame.display.flip()
    clock.tick(FPS)

screen.fill(BLACK)
screen.blit(font.render(f"Game Over! Score: {score}",True,WHITE),(150,180))
pygame.display.flip()
pygame.time.wait(3000)
pygame.quit()
sys.exit()
