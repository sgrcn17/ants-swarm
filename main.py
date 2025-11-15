import pygame
import sys
import random
from ant import Ant
from anthill import AntHill
from foodgroup import FoodGroup
from pheromone import PheromoneManager
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
antCount = 75
foodCount = 500

# Create the ant hill (mrowisko) at the center
ant_hill = AntHill(WIDTH // 2, HEIGHT // 2, radius=40)

# Create pheromone manager
pheromone_manager = PheromoneManager(evaporation_rate=1, influence_radius=80)

# Create ants at the ant hill location
ants = [Ant(WIDTH // 2, HEIGHT // 2, scale, WIDTH, HEIGHT) for _ in range(antCount)]
for ant in ants:
    ant.set_ant_hill(ant_hill)
    ant.set_pheromone_manager(pheromone_manager)

# Create 4 food groups in different corners/areas of the screen
food_groups = []
food_per_group = foodCount // 4
corner_margin = 90  # Distance from corner (10px from border + spread_radius of 80)

# Group 0: Top-left corner
food_groups.append(FoodGroup(0, corner_margin, corner_margin, food_per_group, spread_radius=80))

# Group 1: Top-right corner
food_groups.append(FoodGroup(1, WIDTH - corner_margin, corner_margin, food_per_group, spread_radius=80))

# Group 2: Bottom-left corner
food_groups.append(FoodGroup(2, corner_margin, HEIGHT - corner_margin, food_per_group, spread_radius=80))

# Group 3: Bottom-right corner
food_groups.append(FoodGroup(3, WIDTH - corner_margin, HEIGHT - corner_margin, food_per_group, spread_radius=80))

clock = pygame.time.Clock()

while running:
    deltaTime = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(COLOR.GROUND)

    # Update pheromones (evaporation)
    pheromone_manager.update(deltaTime)

    # Draw pheromones first (behind everything)
    pheromone_manager.draw(screen, scale)

    # Draw the ant hill first (so it appears behind ants)
    ant_hill.draw(screen)

    # Collect all food positions from all groups for ant vision
    all_food_positions = []
    for group in food_groups:
        all_food_positions.extend(group.get_all_positions())

    # Update and draw ants
    for ant in ants:
        # Check if ant reached food (increased collision radius)
        if not ant.carrying_food and ant.seenFood is not None:
            for group in food_groups:
                if ant.seenFood in group.get_all_positions():
                    if (ant.position - ant.seenFood).length() < 15:  # Increased from 5 to 15
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