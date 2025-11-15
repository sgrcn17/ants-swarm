import pygame
import random
import math
from parameters import COLOR

class Ant:
    def __init__(self, x, y, scale=1.0, map_width=1000, map_height=1000):
        self.rotation = 0.0
        self.scale = scale
        self.maxSpeed = 7
        self.steerStrength = 20
        self.wanderStrength = 0.5
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(1, 0)
        self.desiredDirection = pygame.math.Vector2(1, 0)
        self.viewDistance = 70 * scale
        self.viewAngle = 3.14159 / 2
        self.seenFood = None
        self.carrying_food = False
        self.food_group_id = None
        self.ant_hill = None
        self.map_width = map_width
        self.map_height = map_height
        self.pheromone_manager = None
        self.pheromone_deposit_timer = 0.0
        self.pheromone_deposit_interval = 0.1  # Drop pheromone every 0.1 seconds
        self.pheromone_follow_probability = 0.85  # 85% chance to follow pheromones
        self.pheromone_influence_weight = 0.7  # How much pheromones affect direction (increased)
        self.distance_from_hill = 0.0  # Track distance traveled from ant hill
        self.min_distance_to_follow = 60  # Minimum distance from hill before following pheromones (reduced)
        self.path_memory = []  # Store path when finding food
        self.max_path_memory = 200  # Maximum path points to remember
        self.wanderStrength = 0.5  # Reduced wander for more focused following
        self.last_pheromone_direction = None  # Track last pheromone direction for momentum
        self.steps_since_food = 0  # Track how long since leaving ant hill
    
    def seeFood(self, foodPositions):
        # If carrying food, don't look for more food
        if self.carrying_food:
            self.seenFood = None
            return
        
        if self.seenFood not in foodPositions:
            self.seenFood = None
    
        for foodPos in foodPositions:
            toFood = pygame.math.Vector2(foodPos) - self.position
            distance = toFood.length()
            if distance > self.viewDistance:
                continue
            angleToFood = self.velocity.angle_to(toFood)
            if abs(angleToFood) < math.degrees(self.viewAngle) / 2:
                self.seenFood = foodPos
                return
    
    def set_ant_hill(self, ant_hill):
        """Set the ant hill reference for this ant"""
        self.ant_hill = ant_hill
    
    def set_pheromone_manager(self, pheromone_manager):
        """Set the pheromone manager reference for this ant"""
        self.pheromone_manager = pheromone_manager
    
    def pickup_food(self, group_id):
        """Pick up food and remember which group it came from"""
        self.carrying_food = True
        self.food_group_id = group_id
        self.seenFood = None
        self.steps_since_food = 0
    
    def deposit_food(self):
        """Deposit food at the ant hill"""
        if self.ant_hill and self.carrying_food:
            self.ant_hill.deposit_food(self.food_group_id)
            
            # Clear path memory for next trip
            self.path_memory.clear()
            self.carrying_food = False
            self.food_group_id = None
            self.last_pheromone_direction = None
            self.steps_since_food = 0
            return True
        return False
    

    def update(self, deltaTime):
        # Update distance from ant hill
        if self.ant_hill:
            self.distance_from_hill = (self.position - self.ant_hill.position).length()
        
        # Deposit pheromones at regular intervals based on state
        self.pheromone_deposit_timer += deltaTime
        if self.pheromone_deposit_timer >= self.pheromone_deposit_interval:
            if self.distance_from_hill > 40 and self.pheromone_manager:
                if self.carrying_food:
                    # Deposit RED pheromone when carrying food (successful path back)
                    self.pheromone_manager.add_pheromone(
                        self.position.x, self.position.y, 'return', strength=3.0
                    )
                # Blue pheromones temporarily removed
            self.pheromone_deposit_timer = 0.0
        
        # Record path when searching (not carrying food)
        if not self.carrying_food and self.distance_from_hill > 50:
            # Add current position to path memory (limit size)
            if len(self.path_memory) == 0 or (self.position - self.path_memory[-1]).length() > 10:
                self.path_memory.append(self.position.copy())
                if len(self.path_memory) > self.max_path_memory:
                    self.path_memory.pop(0)  # Remove oldest
        
        # Determine desired direction based on state and pheromones
        base_direction = pygame.math.Vector2(0, 0)
        can_follow_pheromones = self.distance_from_hill > self.min_distance_to_follow
        
        # If carrying food, head back to ant hill
        if self.carrying_food and self.ant_hill:
            toHill = self.ant_hill.position - self.position
            base_direction = toHill.normalize()
            # Go directly home in a straight line - no steering or blending
        
        elif self.seenFood is not None:
            # Going toward visible food
            toFood = pygame.math.Vector2(self.seenFood) - self.position
            base_direction = toFood.normalize()
        else:
            # SEARCHING: Follow RED pheromones (paths from ants returning with food)
            # Important: Follow them in REVERSE (away from ant hill, toward food)
            followed_pheromone = False
            self.steps_since_food += 1
            
            if self.pheromone_manager and can_follow_pheromones and random.random() < self.pheromone_follow_probability:
                # Get best pheromone direction that leads AWAY from ant hill
                best_direction = None
                best_score = -1
                
                nearby_pheromones = self.pheromone_manager.get_nearby_pheromones(
                    self.position, 'return', self.pheromone_manager.influence_radius
                )
                
                if nearby_pheromones and self.ant_hill:
                    hill_direction = (self.ant_hill.position - self.position).normalize()
                    
                    for pheromone in nearby_pheromones:
                        to_pheromone = (pheromone.position - self.position)
                        distance = to_pheromone.length()
                        
                        if distance > 5:  # Ignore very close pheromones
                            direction = to_pheromone.normalize()
                            
                            # Prefer pheromones that are AWAY from ant hill
                            away_score = -direction.dot(hill_direction)  # Negative dot = away from hill
                            
                            # Prefer stronger pheromones
                            strength_score = pheromone.strength
                            
                            # Prefer pheromones in current movement direction (momentum)
                            momentum_score = 0
                            if self.last_pheromone_direction:
                                momentum_score = direction.dot(self.last_pheromone_direction) * 0.5
                            
                            # Combined score
                            total_score = away_score * 2.0 + strength_score * 0.3 + momentum_score
                            
                            if total_score > best_score:
                                best_score = total_score
                                best_direction = direction
                    
                    if best_direction and best_score > 0:
                        base_direction = best_direction
                        self.last_pheromone_direction = best_direction
                        followed_pheromone = True
            
            # Add wandering behavior if not following pheromones
            if not followed_pheromone:
                self.last_pheromone_direction = None
                if base_direction.length() == 0:
                    base_direction = self.desiredDirection
                
                angle = random.uniform(0, 2 * 3.14159)
                radius = random.uniform(0, 1)
                randomDirection = pygame.math.Vector2(radius * pygame.math.Vector2(1, 0).rotate_rad(angle))
                base_direction = (base_direction + randomDirection * self.wanderStrength).normalize()
        
        # Ensure base direction is normalized for consistent speed
        if base_direction.length() > 0:
            self.desiredDirection = base_direction.normalize()
        else:
            self.desiredDirection = base_direction
        
        # When carrying food, move in perfectly straight line to ant hill
        if self.carrying_food and self.ant_hill:
            # Set velocity directly toward ant hill for straight-line movement
            toHill = self.ant_hill.position - self.position
            if toHill.length() > 0:
                self.velocity = toHill.normalize() * self.maxSpeed
        else:
            # Normal steering behavior for searching ants
            desiredVelocity = self.desiredDirection * self.maxSpeed
            desiredSteeringForce = desiredVelocity - self.velocity
            
            acceleration = pygame.math.Vector2(desiredSteeringForce)
            if acceleration.length() > self.steerStrength:
                acceleration.scale_to_length(self.steerStrength)
            
            self.velocity += acceleration * deltaTime
            if self.velocity.length() > self.maxSpeed:
                self.velocity.scale_to_length(self.maxSpeed)

        self.position += self.velocity

        # Boundary collision detection - keep ants within map
        margin = 10  # Small margin from edge
        bounced = False
        
        if self.position.x < margin:
            self.position.x = margin
            self.velocity.x = abs(self.velocity.x)  # Bounce right
            bounced = True
        elif self.position.x > self.map_width - margin:
            self.position.x = self.map_width - margin
            self.velocity.x = -abs(self.velocity.x)  # Bounce left
            bounced = True
            
        if self.position.y < margin:
            self.position.y = margin
            self.velocity.y = abs(self.velocity.y)  # Bounce down
            bounced = True
        elif self.position.y > self.map_height - margin:
            self.position.y = self.map_height - margin
            self.velocity.y = -abs(self.velocity.y)  # Bounce up
            bounced = True

        # Collision detection with ant hill
        if self.ant_hill:
            distance_to_hill = (self.position - self.ant_hill.position).length()
            # If ant is too close to hill center (but not depositing food)
            if distance_to_hill < self.ant_hill.radius:
                # Push ant back outside the hill
                direction_from_hill = (self.position - self.ant_hill.position)
                if direction_from_hill.length() > 0:
                    direction_from_hill = direction_from_hill.normalize()
                    self.position = self.ant_hill.position + direction_from_hill * self.ant_hill.radius
                    # Bounce velocity away from hill
                    self.velocity = direction_from_hill * self.maxSpeed * 0.5

        if self.velocity.length() > 0:
            self.rotation = self.velocity.angle_to(pygame.math.Vector2(1, 0))

    def draw(self, screen):
        # Determine ant color based on whether it's carrying food
        ant_color = COLOR.ANT_CARRYING if self.carrying_food else COLOR.ANT
        
        ant_surface = pygame.Surface((20 * self.scale, 7 * self.scale), pygame.SRCALPHA)
        pygame.draw.ellipse(ant_surface, ant_color, (0, 0, 20 * self.scale, 7 * self.scale))
        rotated_surface = pygame.transform.rotate(ant_surface, self.rotation)
        rotated_rect = rotated_surface.get_rect(center=(self.position.x, self.position.y))
        screen.blit(rotated_surface, rotated_rect.topleft)

