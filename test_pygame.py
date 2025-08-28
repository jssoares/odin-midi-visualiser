import pygame
import sys
import math
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
EARTH_COLOR = (139, 69, 19)  # Brown like your earth element
EARTH_BRIGHT = (200, 120, 50)  # Brighter brown for crystals

def draw_diamond(surface, center_x, center_y, size, color, opacity=255):
    """Draw a diamond shape using pygame.draw.polygon"""
    # Diamond vertices (top, right, bottom, left)
    diamond_points = [
        (center_x, center_y - size),        # Top
        (center_x + size, center_y),        # Right
        (center_x, center_y + size),        # Bottom
        (center_x - size, center_y)         # Left
    ]
    
    # Handle opacity by creating a surface with alpha
    if opacity < 255:
        # Create a surface with per-pixel alpha
        diamond_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        pygame.draw.polygon(diamond_surface, (*color, opacity), 
                          [(p[0] - center_x + size * 1.5, p[1] - center_y + size * 1.5) for p in diamond_points])
        surface.blit(diamond_surface, (center_x - size * 1.5, center_y - size * 1.5))
    else:
        # Direct drawing for full opacity
        pygame.draw.polygon(surface, color, diamond_points)

def draw_crystals(surface, center_x, center_y, base_size, intensity, color):
    """Draw crystal spikes around the diamond"""
    crystal_positions = [
        (base_size * 1.2, 0),           # Right
        (-base_size * 1.2, 0),          # Left  
        (0, -base_size * 1.2),          # Top
        (0, base_size * 1.2),           # Bottom
        (base_size * 0.8, -base_size * 0.8),   # Top-right
        (-base_size * 0.8, -base_size * 0.8),  # Top-left
        (base_size * 0.8, base_size * 0.8),    # Bottom-right
        (-base_size * 0.8, base_size * 0.8)    # Bottom-left
    ]
    
    for dx, dy in crystal_positions:
        if intensity > 0.1:  # Only show crystals when there's activity
            crystal_x = center_x + dx
            crystal_y = center_y + dy
            crystal_height = int(16 + intensity * 12)
            crystal_width = 6
            
            # Draw crystal as rectangle
            crystal_rect = pygame.Rect(
                crystal_x - crystal_width // 2,
                crystal_y - crystal_height // 2,
                crystal_width,
                crystal_height
            )
            
            crystal_opacity = int(intensity * 220)
            if crystal_opacity > 0:
                crystal_surface = pygame.Surface((crystal_width, crystal_height), pygame.SRCALPHA)
                pygame.draw.rect(crystal_surface, (*color, crystal_opacity), 
                               (0, 0, crystal_width, crystal_height))
                surface.blit(crystal_surface, (crystal_rect.x, crystal_rect.y))

def main():
    # Create the display
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pygame Diamond Polygon Test")
    clock = pygame.time.Clock()
    
    # Animation variables
    start_time = time.time()
    
    print("🎮 Pygame Diamond Test")
    print("Controls:")
    print("  SPACE - Toggle crystal activity")
    print("  ESC - Exit")
    print("  Mouse - Move diamond")
    
    crystal_active = False
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    crystal_active = not crystal_active
                    print(f"Crystal activity: {'ON' if crystal_active else 'OFF'}")
        
        # Get mouse position for diamond center
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Animation values
        current_time = time.time() - start_time
        pulse = (math.sin(current_time * 3) + 1) / 2  # 0 to 1
        
        # Clear screen
        screen.fill(WHITE)  # White background like your app
        
        # Draw diamond
        diamond_size = 40 + int(pulse * 20) if crystal_active else 40
        diamond_opacity = 160
        
        draw_diamond(screen, mouse_x, mouse_y, diamond_size, EARTH_COLOR, diamond_opacity)
        
        # Draw crystals if active
        if crystal_active:
            crystal_intensity = 0.5 + pulse * 0.5  # 0.5 to 1.0
            draw_crystals(screen, mouse_x, mouse_y, diamond_size, crystal_intensity, EARTH_BRIGHT)
        
        # Draw info text
        font = pygame.font.Font(None, 36)
        info_text = font.render(f"Diamond Size: {diamond_size}, Crystals: {'ON' if crystal_active else 'OFF'}", 
                               True, BLACK)
        screen.blit(info_text, (10, 10))
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()