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
    
    def seeFood(self, foodPositions):
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

    def update(self, deltaTime):
        if self.seenFood is not None:
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
        ant_surface = pygame.Surface((20 * self.scale, 7 * self.scale), pygame.SRCALPHA)
        pygame.draw.ellipse(ant_surface, COLOR.ANT, (0, 0, 20 * self.scale, 7 * self.scale))
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

