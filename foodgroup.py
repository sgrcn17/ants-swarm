import pygame
import random
import math
from parameters import COLOR

class FoodGroup:
    """
    Represents a cluster/group of food items positioned together.
    This allows organizing food into distinct areas for ACO algorithm preparation.
    """
    def __init__(self, group_id, center_x, center_y, food_count, spread_radius=50):
        self.group_id = group_id
        self.center = pygame.math.Vector2(center_x, center_y)
        self.spread_radius = spread_radius
        self.food_items = []
        self.color = COLOR.FOOD_GROUPS[group_id % len(COLOR.FOOD_GROUPS)]
        
        # Generate food items around the center
        for _ in range(food_count):
            # Random position within spread radius
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, spread_radius)
            offset_x = distance * math.cos(angle)
            offset_y = distance * math.sin(angle)
            
            food_pos = pygame.math.Vector2(center_x + offset_x, center_y + offset_y)
            self.food_items.append(food_pos)
    
    def remove_food(self, position):
        """Remove a food item at the given position"""
        for food_pos in self.food_items:
            if (food_pos - position).length() < 1:  # Close enough
                self.food_items.remove(food_pos)
                return True
        return False
    
    def get_nearest_food(self, position, max_distance=None):
        """Find the nearest food item to a given position"""
        if not self.food_items:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for food_pos in self.food_items:
            distance = (food_pos - position).length()
            if distance < min_distance:
                if max_distance is None or distance <= max_distance:
                    min_distance = distance
                    nearest = food_pos
        
        return nearest
    
    def is_empty(self):
        """Check if all food has been collected"""
        return len(self.food_items) == 0
    
    def get_food_count(self):
        """Get the number of remaining food items"""
        return len(self.food_items)
    
    def draw(self, screen, scale=1.0):
        """Draw all food items in this group"""
        for food_pos in self.food_items:
            pygame.draw.circle(screen, self.color, 
                             (int(food_pos.x), int(food_pos.y)), 
                             int(5 * scale))
    
    def get_all_positions(self):
        """Get all food positions (for ant vision)"""
        return self.food_items.copy()
