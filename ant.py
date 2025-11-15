import pygame
import random
import math
from parameters import COLOR

class Ant:
    def __init__(self, x, y, scale=1.0):
        self.rotation = 0.0
        self.scale = scale
        self.maxSpeed = 7
        self.steerStrength = 20
        self.wanderStrength = 1
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(1, 0)
        self.desiredDirection = pygame.math.Vector2(1, 0)
        self.viewDistance = 70 * scale
        self.viewAngle = 3.14159 / 2
        self.seenFood = None
        self.carrying_food = False
        self.food_group_id = None
        self.ant_hill = None
    
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
    
    def pickup_food(self, group_id):
        """Pick up food and remember which group it came from"""
        self.carrying_food = True
        self.food_group_id = group_id
        self.seenFood = None
    
    def deposit_food(self):
        """Deposit food at the ant hill"""
        if self.ant_hill and self.carrying_food:
            self.ant_hill.deposit_food(self.food_group_id)
            self.carrying_food = False
            self.food_group_id = None
            return True
        return False

    def update(self, deltaTime):
        # If carrying food, head back to ant hill
        if self.carrying_food and self.ant_hill:
            toHill = self.ant_hill.position - self.position
            self.desiredDirection = toHill.normalize()
        elif self.seenFood is not None:
            toFood = pygame.math.Vector2(self.seenFood) - self.position
            self.desiredDirection = toFood.normalize()
        else:
            angle = random.uniform(0, 2 * 3.14159)
            radius = random.uniform(0, 1)
            randomDirection = pygame.math.Vector2(radius * pygame.math.Vector2(1, 0).rotate_rad(angle))
            self.desiredDirection = (self.desiredDirection + randomDirection * self.wanderStrength).normalize()
        
        desiredVelocity = self.desiredDirection * self.maxSpeed
        desiredSteeringForce = desiredVelocity - self.velocity
        
        acceleration = pygame.math.Vector2(desiredSteeringForce)
        if acceleration.length() > self.steerStrength:
            acceleration.scale_to_length(self.steerStrength)
        
        self.velocity += acceleration * deltaTime
        if self.velocity.length() > self.maxSpeed:
            self.velocity.scale_to_length(self.maxSpeed)

        self.position += self.velocity

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

        angleCoeff = 90 / 3.14159
        segmentsCount = 16
        points = [self.position]
        
        start_rad = math.radians(-self.rotation + self.viewAngle * angleCoeff)
        end_rad = math.radians(-self.rotation - self.viewAngle * angleCoeff)

        for i in range(segmentsCount + 1):
            angle = start_rad + (end_rad - start_rad) * i / segmentsCount
            x = self.position.x + self.viewDistance * math.cos(angle)
            y = self.position.y + self.viewDistance * math.sin(angle)
            points.append((x, y))
        
        pygame.draw.polygon(screen, COLOR.ANTVIEW, points)

