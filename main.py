import pygame
import sys
import random
from ant import Ant
from anthill import AntHill
from foodgroup import FoodGroup
from parameters import COLOR

pygame.init()

WIDTH = 1000
HEIGHT = 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ant Simulation")

# Font for statistics
font = pygame.font.Font(None, 24)

clock = pygame.time.Clock()

running = True

scale = 0.5
antCount = 100
foodCount = 100

# Create the ant hill (mrowisko) at the center
ant_hill = AntHill(WIDTH // 2, HEIGHT // 2, radius=40)

# Create ants at the ant hill location
ants = [Ant(WIDTH // 2, HEIGHT // 2, scale) for _ in range(antCount)]
for ant in ants:
    ant.set_ant_hill(ant_hill)

# Create 4 food groups in different corners/areas of the screen
food_groups = []
food_per_group = foodCount // 4

# Group 0: Top-left area
food_groups.append(FoodGroup(0, WIDTH * 0.25, HEIGHT * 0.25, food_per_group, spread_radius=80))

# Group 1: Top-right area
food_groups.append(FoodGroup(1, WIDTH * 0.75, HEIGHT * 0.25, food_per_group, spread_radius=80))

# Group 2: Bottom-left area
food_groups.append(FoodGroup(2, WIDTH * 0.25, HEIGHT * 0.75, food_per_group, spread_radius=80))

# Group 3: Bottom-right area
food_groups.append(FoodGroup(3, WIDTH * 0.75, HEIGHT * 0.75, food_per_group, spread_radius=80))

clock = pygame.time.Clock()

while running:
    deltaTime = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(COLOR.GROUND)

    # Draw the ant hill first (so it appears behind ants)
    ant_hill.draw(screen)

    # Collect all food positions from all groups for ant vision
    all_food_positions = []
    for group in food_groups:
        all_food_positions.extend(group.get_all_positions())

    # Update and draw ants
    for ant in ants:
        # Check if ant reached food
        if not ant.carrying_food and ant.seenFood is not None:
            for group in food_groups:
                if ant.seenFood in group.get_all_positions():
                    if (ant.position - ant.seenFood).length() < 5:
                        group.remove_food(ant.seenFood)
                        ant.pickup_food(group.group_id)
                        break
        
        # Check if ant carrying food reached the ant hill
        if ant.carrying_food and ant_hill.is_inside(ant.position, distance_threshold=50):
            ant.deposit_food()
        
        # Update ant behavior
        ant.seeFood(all_food_positions)
        ant.update(deltaTime)
        ant.draw(screen)

    # Draw all food groups
    for group in food_groups:
        group.draw(screen, scale)
    
    # Draw statistics
    ant_hill.draw_statistics(screen, font)

    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()
sys.exit()