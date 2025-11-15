import pygame
import math
from parameters import COLOR

class Pheromone:
    """
    Represents a single pheromone marker dropped by an ant.
    Pheromones evaporate over time and influence ant movement.
    """
    def __init__(self, x, y, pheromone_type, initial_strength=1.0):
        self.position = pygame.math.Vector2(x, y)
        self.type = pheromone_type  # 'search' (blue) or 'return' (red)
        self.strength = initial_strength
        self.max_strength = initial_strength
        
    def evaporate(self, evaporation_rate, deltaTime):
        """Reduce pheromone strength over time"""
        self.strength -= evaporation_rate * deltaTime
        return self.strength > 0.05  # Return True if still viable (increased threshold)
    
    def get_influence(self, position, max_distance):
        """Calculate influence of this pheromone on a position"""
        distance = (self.position - position).length()
        if distance > max_distance:
            return 0.0
        # Influence decreases with distance
        influence = self.strength * (1.0 - distance / max_distance)
        return max(0.0, influence)
    
    def draw(self, screen, scale=1.0):
        """Draw the pheromone as a colored dot"""
        color = COLOR.PHEROMONE_SEARCH if self.type == 'search' else COLOR.PHEROMONE_RETURN
        # Alpha based on strength
        alpha = int(min(255, self.strength * 255))
        radius = int(3 * scale)
        
        # Create surface with alpha
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        color_with_alpha = (*color, alpha)
        pygame.draw.circle(surf, color_with_alpha, (radius, radius), radius)
        screen.blit(surf, (int(self.position.x - radius), int(self.position.y - radius)))


class PheromoneManager:
    """
    Manages all pheromones in the simulation.
    Handles evaporation, influence calculations, and rendering.
    """
    def __init__(self, evaporation_rate=0.3, influence_radius=50):
        self.pheromones = []
        self.evaporation_rate = evaporation_rate
        self.influence_radius = influence_radius
        
    def add_pheromone(self, x, y, pheromone_type, strength=1.0):
        """Add a new pheromone to the system"""
        pheromone = Pheromone(x, y, pheromone_type, strength)
        self.pheromones.append(pheromone)
    
    def update(self, deltaTime):
        """Update all pheromones (evaporation)"""
        self.pheromones = [p for p in self.pheromones 
                          if p.evaporate(self.evaporation_rate, deltaTime)]
    
    def get_pheromone_influence(self, position, pheromone_type):
        """
        Calculate the direction and strength of pheromone influence at a position.
        Returns a direction vector weighted by pheromone strength.
        """
        influence_vector = pygame.math.Vector2(0, 0)
        total_weight = 0.0
        
        for pheromone in self.pheromones:
            if pheromone.type != pheromone_type:
                continue
                
            influence = pheromone.get_influence(position, self.influence_radius)
            if influence > 0:
                direction = (pheromone.position - position)
                if direction.length() > 0:
                    direction = direction.normalize()
                    influence_vector += direction * influence
                    total_weight += influence
        
        if total_weight > 0:
            # Normalize by total weight to get average direction
            influence_vector = influence_vector / total_weight
            # Return direction and strength (0 to 1)
            strength = min(1.0, total_weight)
            return influence_vector, strength
        
        return pygame.math.Vector2(0, 0), 0.0
    
    def get_nearby_pheromones(self, position, pheromone_type, radius):
        """Get all pheromones of a type within a radius"""
        nearby = []
        for pheromone in self.pheromones:
            if pheromone.type == pheromone_type:
                if (pheromone.position - position).length() <= radius:
                    nearby.append(pheromone)
        return nearby
    
    def draw(self, screen, scale=1.0):
        """Draw all pheromones"""
        for pheromone in self.pheromones:
            pheromone.draw(screen, scale)
    
    def get_count(self):
        """Get total pheromone count"""
        return len(self.pheromones)
    
    def get_count_by_type(self, pheromone_type):
        """Get count of specific pheromone type"""
        return sum(1 for p in self.pheromones if p.type == pheromone_type)
