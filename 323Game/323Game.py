import math
import random
import pygame
import os

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
PLAYER_SPEED = 300

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Setup the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

class MusicPlayer(object):
    def __init__(self, music_file):
        pygame.mixer.init()
        self.music_file = music_file
        self.is_playing = False

    def play(self):
        if not self.is_playing:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.is_playing = True

    def stop(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, position, frames, animation_speed=0.1):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.animation_speed = animation_speed
        self.animation_time = 0
        self.image = frames[self.current_frame]
        self.rect = self.image.get_rect(center=position)
        self.pos = pygame.Vector2(position)
        self.direction = pygame.Vector2(0, 0)
        
    def update(self, dt):
        # Animation update
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
        
        # Position update
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        self.pos += self.direction * PLAYER_SPEED * dt
        self.rect.center = self.pos
        
        # Keep player on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.pos.x, self.pos.y = self.rect.center

class Player(AnimatedSprite):
    def __init__(self, x, y):
        # Sprite sheet dimensions
        self.sprite_width = 80
        self.sprite_height = 120
        self.cols = 2
        self.rows = 4
        
        # Load sprite sheet and create animation frames
        sprite_sheet = self.load_sprite_sheet("player.png", self.cols, self.rows)
        
        # Organize animations by direction (assuming sprite sheet organization)
        # Row 0: Down animation (2 frames)
        # Row 1: Left animation (2 frames)
        # Row 2: Right animation (2 frames)
        # Row 3: Up animation (2 frames)
        self.animations = { #all 2 frames
            "down": sprite_sheet[0:2],
            "left": sprite_sheet[2:4],
            "right": sprite_sheet[4:6],
            "up": sprite_sheet[6:8]
        }
        
        super().__init__((x, y), self.animations["down"])
        self.current_animation = "down"
        self.last_direction = "down"
        self.speed = PLAYER_SPEED
        
    def load_sprite_sheet(self, filename, cols, rows):
        try:
            full_path = os.path.join("Sprites", filename)
            sprite_sheet = pygame.image.load(full_path).convert_alpha()
        except:
            # Fallback: create a placeholder sprite sheet if the file isn't found
            print(f"Warning: Could not load {filename}, using placeholder")
            sprite_sheet = pygame.Surface((cols * self.sprite_width, rows * self.sprite_height), pygame.SRCALPHA)
            for row in range(rows):
                for col in range(cols):
                    x = col * self.sprite_width
                    y = row * self.sprite_height
                    color = (row * 60 % 255, 100 + col * 30 % 155, 50 + (row + col) * 20 % 205)
                    pygame.draw.rect(sprite_sheet, color, (x, y, self.sprite_width, self.sprite_height))
                    pygame.draw.rect(sprite_sheet, BLACK, (x, y, self.sprite_width, self.sprite_height), 1)
                    # Draw direction indicator
                    font = pygame.font.SysFont(None, 20)
                    direction = ["Down", "Left", "Right", "Up"][row]
                    text = font.render(f"{direction} {col+1}", True, BLACK)
                    sprite_sheet.blit(text, (x + 5, y + 5))
        
        frames = []
        for row in range(rows):
            for col in range(cols):
                frame = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
                frame.blit(sprite_sheet, (0, 0),
                          (col * self.sprite_width,
                           row * self.sprite_height,
                           self.sprite_width,
                           self.sprite_height))
                frames.append(frame)
        
        return frames

# The rest of your game loop remains the same
    
    def update(self, dt):
        # Get keyboard input
        keys = pygame.key.get_pressed()
        move_vec = pygame.Vector2(0, 0)
        
        if keys[pygame.K_w]:
            move_vec.y -= 1
            self.last_direction = "up"
        if keys[pygame.K_s]:
            move_vec.y += 1
            self.last_direction = "down"
        if keys[pygame.K_a]:
            move_vec.x -= 1
            self.last_direction = "left"
        if keys[pygame.K_d]:
            move_vec.x += 1
            self.last_direction = "right"
            
        self.direction = move_vec
        
        # Change animation if direction changed
        if move_vec.length() > 0:
            if abs(move_vec.x) > abs(move_vec.y):
                self.current_animation = "left" if move_vec.x < 0 else "right"
            else:
                self.current_animation = "up" if move_vec.y < 0 else "down"
            
            # Update frames if animation changed
            if self.frames != self.animations[self.current_animation]:
                self.frames = self.animations[self.current_animation]
                self.current_frame = 0
        else:
            # When not moving, show first frame of last direction
            if self.frames != self.animations[self.last_direction]:
                self.frames = self.animations[self.last_direction]
                self.current_frame = 0
        
        super().update(dt)

class Mob(AnimatedSprite):
    def __init__(self, x, y):
        # Sprite sheet dimensions
        self.sprite_width = 64
        self.sprite_height = 64
        self.cols = 4
        self.rows = 1

        # Starting position of the mob
        self.rect = pygame.Rect(x, y, self.sprite_width, self.sprite_height)
        
        # Load sprite sheet and create animation frames
        sprite_sheet = self.load_sprite_sheet("Golem_Run.png", self.cols, self.rows)
        
        # Organize animations by direction
        self.animations = {
            "down": sprite_sheet[0:2],
            "left": sprite_sheet[2:4],
            "right": sprite_sheet[4:6],
            "up": sprite_sheet[6:8]
        }
        
        super().__init__((x, y), self.animations["down"])

        # Speed of mob
        self.speed = 1.5  # Fixed speed for simplicity

    def load_sprite_sheet(self, filename, cols, rows):
        try:
            full_path = os.path.join("Sprites", filename)
            sprite_sheet = pygame.image.load(full_path).convert_alpha()
        except:
            # Fallback: create a placeholder sprite sheet if the file isn't found
            print(f"Warning: Could not load {filename}, using placeholder")
            sprite_sheet = pygame.Surface((cols * self.sprite_width, rows * self.sprite_height), pygame.SRCALPHA)
            for row in range(rows):
                for col in range(cols):
                    x = col * self.sprite_width
                    y = row * self.sprite_height
                    color = (row * 60 % 255, 100 + col * 30 % 155, 50 + (row + col) * 20 % 205)
                    pygame.draw.rect(sprite_sheet, color, (x, y, self.sprite_width, self.sprite_height))
                    pygame.draw.rect(sprite_sheet, (0, 0, 0), (x, y, self.sprite_width, self.sprite_height), 1)
        frames = []
        for row in range(rows):
            for col in range(cols):
                frame = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
                frame.blit(sprite_sheet, (0, 0),
                          (col * self.sprite_width,
                           row * self.sprite_height,
                           self.sprite_width,
                           self.sprite_height))
                frames.append(frame)
        return frames

    def update(self, dt, player):
        # Get the direction to the player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        
        # Calculate distance to the player
        distance = math.sqrt(dx**2 + dy**2)

        # Prevent division by zero if distance is zero (same position)
        if distance != 0:
            # Normalize direction (unit vector)
            dx /= distance
            dy /= distance

            # Update the mob's position to move towards the player
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

        # If mob moves out of screen, reset position to top
        if self.rect.top > SCREEN_HEIGHT + 15 or self.rect.left < -15 or self.rect.right > SCREEN_WIDTH + 15:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.sprite_width)
            self.rect.y = random.randrange(-100, -50)


# Game setup
all_sprites = pygame.sprite.Group()
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
all_sprites.add(player)

music = MusicPlayer("2.Aria of the Soul(P4aa).mp3")
music.play()

mobs = pygame.sprite.Group()
for i in range(5):
    mob = Mob(i * 100 + 100, i * 100 + 100)
    all_sprites.add(mob)
    mobs.add(mob)

# Game loop
running = True
dt = 0  # Delta time

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Update
    #all_sprites.update(dt)
    player.update(dt)
    for mob in mobs:
        mob.update(dt, player)
    
    # Render
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # Debug info
    #font = pygame.font.SysFont(None, 36)
    #debug_text = f"FPS: {int(clock.get_fps())} | Pos: {int(player.pos.x)}, {int(player.pos.y)}"
    #debug_surface = font.render(debug_text, True, GREEN)
    #screen.blit(debug_surface, (10, 10))
    
    # Flip display
    pygame.display.flip()
    
    # Cap FPS and get delta time
    dt = clock.tick(FPS) / 1000
    collisions = pygame.sprite.spritecollide(player, mobs, False)
    # check collisions for game window
    if collisions:
        running = False


pygame.quit()