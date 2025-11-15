import pygame
from parameters import COLOR

class AntHill:
    """
    Mrowisko - the ant colony's nest where ants start and deposit collected food.
    Tracks statistics about food collection.
    """
    def __init__(self, x, y, radius=30):
        self.position = pygame.math.Vector2(x, y)
        self.radius = radius
        self.total_food_collected = 0
        self.food_by_group = {}  # Track food collected from each group
        
    def is_inside(self, position, distance_threshold=None):
        """Check if a position is inside the ant hill"""
        threshold = distance_threshold if distance_threshold else self.radius
        return (position - self.position).length() < threshold
    
    def deposit_food(self, group_id=None):
        """Register food being deposited at the ant hill"""
        self.total_food_collected += 1
        if group_id is not None:
            if group_id not in self.food_by_group:
                self.food_by_group[group_id] = 0
            self.food_by_group[group_id] += 1
    
    def get_statistics(self):
        """Get statistics about collected food"""
        return {
            'total': self.total_food_collected,
            'by_group': self.food_by_group.copy()
        }
    
    def draw(self, screen):
        """Draw the ant hill on the screen"""
        # Draw outer circle (darker)
        pygame.draw.circle(screen, COLOR.ANTHILL_OUTER, 
                         (int(self.position.x), int(self.position.y)), 
                         int(self.radius))
        # Draw inner circle (lighter)
        pygame.draw.circle(screen, COLOR.ANTHILL_INNER, 
                         (int(self.position.x), int(self.position.y)), 
                         int(self.radius * 0.7))
        # Draw center dot
        pygame.draw.circle(screen, COLOR.ANTHILL_CENTER, 
                         (int(self.position.x), int(self.position.y)), 
                         int(self.radius * 0.3))
    
    def draw_statistics(self, screen, font):
        """Draw statistics text on the screen"""
        y_offset = 10
        # Total food
        total_text = font.render(f"Total Food: {self.total_food_collected}", True, (0, 0, 0))
        screen.blit(total_text, (10, y_offset))
        y_offset += 25
        
        # Food by group
        for group_id in sorted(self.food_by_group.keys()):
            count = self.food_by_group[group_id]
            group_text = font.render(f"Group {group_id}: {count}", True, (0, 0, 0))
            screen.blit(group_text, (10, y_offset))
            y_offset += 25
