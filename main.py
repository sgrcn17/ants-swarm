import pygame
import sys
import random
import math
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
foodCount = 1500

# Create the ant hill (mrowisko) close to center but asymmetric
ant_hill = AntHill(WIDTH // 2 + 80, HEIGHT // 2 - 60, radius=40)

# Create pheromone manager
pheromone_manager = PheromoneManager(evaporation_rate=1, influence_radius=80)

# Create ants at the ant hill location with highly asymmetric initial states
ants = [Ant(WIDTH // 2 + 80, HEIGHT // 2 - 60, scale, WIDTH, HEIGHT) for _ in range(antCount)]
for i, ant in enumerate(ants):
    ant.set_ant_hill(ant_hill)
    ant.set_pheromone_manager(pheromone_manager)
    
    # Highly asymmetric initialization
    # Use different random distributions for each ant
    random_angle = random.gauss(0, 3)  # Gaussian distribution for angle clustering
    random_speed = random.triangular(ant.maxSpeed * 0.3, ant.maxSpeed * 1.2, ant.maxSpeed * 0.6)
    
    # Add chaos with prime number offset for each ant
    chaos_offset = (i * 37) % 360  # Prime-based offset
    random_angle += math.radians(chaos_offset)
    
    ant.velocity = pygame.math.Vector2(
        random_speed * math.cos(random_angle),
        random_speed * math.sin(random_angle)
    )
    ant.desiredDirection = ant.velocity.normalize()
    
    # Highly varied rotation
    ant.rotation = random.gauss(0, 120)
    
    # Randomize wander strength per ant for different exploration patterns
    ant.wanderStrength = random.uniform(0.2, 1.5)

# Create 5 food groups asymmetrically placed on the map
# Anthill is at (580, 440)
food_groups = []
food_per_group = foodCount // 5

# Group Green: Close to anthill, upper-left
food_groups.append(FoodGroup(0, 380, 280, food_per_group, spread_radius=80))

# Group Red: Far, top-right area
food_groups.append(FoodGroup(1, WIDTH - 180, 200, food_per_group, spread_radius=80))

# Group Blue: Medium distance, left side
food_groups.append(FoodGroup(2, 200, HEIGHT - 300, food_per_group, spread_radius=80))

# Group Yellow: Close to anthill, right side
food_groups.append(FoodGroup(3, 750, 520, food_per_group, spread_radius=80))

# Group Purple: Far, bottom area
food_groups.append(FoodGroup(4, WIDTH // 2 - 100, HEIGHT - 120, food_per_group, spread_radius=80))

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
        
        # Only collect food positions from nearby groups (within vision range)
        nearby_food = []
        vision_range = ant.viewDistance + 100  # Add buffer to check slightly beyond view distance
        for group in food_groups:
            # Quick distance check to group center
            dist_to_group = (ant.position - group.center).length()
            if dist_to_group < vision_range + group.spread_radius:
                nearby_food.extend(group.get_all_positions())
        
        # Update ant behavior with only nearby food
        ant.seeFood(nearby_food)
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