import pygame
import sys
import random
from ant import Ant
from parameters import COLOR

pygame.init()

WIDTH = 1000
HEIGHT = 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ant Simulation")

clock = pygame.time.Clock()

running = True

scale = 0.5
antCount = 100
foodCount = 100

ants = [Ant(WIDTH // 2, HEIGHT // 2, scale) for _ in range(antCount)]
food = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(foodCount)]

clock = pygame.time.Clock()

while running:
    deltaTime = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(COLOR.GROUND)

    for ant in ants:
        for food_pos in food:
            if ((ant.position - pygame.math.Vector2(food_pos))).length() < 5:
                food.remove(food_pos)

    for ant in ants:
        ant.seeFood(food)
        ant.update(deltaTime)
        ant.draw(screen)

    for food_pos in food:
        pygame.draw.circle(screen, COLOR.FOOD, food_pos, 5 * scale)

    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()
sys.exit()