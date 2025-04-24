import math
import random
import pygame
import os
import sys

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
PLAYER_SPEED = 300

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Setup the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Lone Voyager")
clock = pygame.time.Clock()

# Music files
default_music = "2.Aria of the Soul(P4).mp3"
chase_music = "Hollow Knight OST.mp3"

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def show_start_screen():
    screen.fill(BLACK)
    draw_text(screen, "LONE VOYAGER", 64, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, "WASD or Arrow Keys to Move", 36, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text(screen, "Press O to interact with objects", 36, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
    draw_text(screen, "Press any key to begin", 36, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3/4)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYUP:
                waiting = False
    return True

def show_game_over_screen():
    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", 64, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, "Press any key to play again", 36, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYUP:
                waiting = False
    return True

def show_message_screen(message):
    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    
    # Draw the overlay
    screen.blit(overlay, (0, 0))
    
    # Draw message box
    message_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3, 
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    pygame.draw.rect(screen, WHITE, message_rect)
    pygame.draw.rect(screen, BLACK, message_rect, 2)
    
    # Split message into lines that fit in the box
    font = pygame.font.Font(None, 36)
    words = message.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] < message_rect.width - 40:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw each line of text
    y_offset = message_rect.y + 20
    for line in lines:
        draw_text(screen, line, 36, BLACK, SCREEN_WIDTH // 2, y_offset)
        y_offset += 40
    
    # Draw instruction to continue
    draw_text(screen, "Press ENTER to continue", 36, BLACK, SCREEN_WIDTH // 2, message_rect.bottom - 40)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False
    return True

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))

class Sign(pygame.sprite.Sprite):
    def __init__(self, x, y, message):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(YELLOW)
        pygame.draw.rect(self.image, BLACK, (0, 0, 40, 60), 2)
        draw_text(self.image, "!", 30, BLACK, 20, 30)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.message = message
        self.interact_rect = pygame.Rect(x - 50, y - 50, 140, 160)  # Larger area for interaction

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

    def set_Volume(self, volume):
        pygame.mixer.music.set_volume(volume)

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
        self.speed = PLAYER_SPEED
        
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
        
        # Store old position for collision handling
        old_pos = self.pos.copy()
        
        # Update position
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
        
        # Keep sprite on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.pos.x, self.pos.y = self.rect.center
        
        return old_pos

class Player(AnimatedSprite):
    def __init__(self, x, y):
        # Sprite sheet dimensions
        self.sprite_width = 80
        self.sprite_height = 120
        self.cols = 2
        self.rows = 4
        
        # Load sprite sheet and create animation frames
        sprite_sheet = self.load_sprite_sheet("player.png", self.cols, self.rows)
        
        # Organize animations by direction
        self.animations = {
            "down": sprite_sheet[0:2],
            "left": sprite_sheet[2:4],
            "right": sprite_sheet[4:6],
            "up": sprite_sheet[6:8]
        }
        
        super().__init__((x, y), self.animations["down"])
        self.current_animation = "down"
        self.last_direction = "down"
        self.can_interact = False
        self.near_sign = None
        
        # Stun mechanic properties
        self.stun_cooldown = 0
        self.stun_radius = 150
        self.stun_duration = 3.0
        self.stun_cooldown_time = 5.0
        self.stun_sound = None  # You can load a sound file here
        
    def load_sprite_sheet(self, filename, cols, rows):
        try:
            full_path = os.path.join("Sprites", filename)
            sprite_sheet = pygame.image.load(full_path).convert_alpha()
        except:
            # Fallback: create a placeholder sprite sheet
            print(f"Warning: Could not load {filename}, using placeholder")
            sprite_sheet = pygame.Surface((cols * self.sprite_width, rows * self.sprite_height), pygame.SRCALPHA)
            for row in range(rows):
                for col in range(cols):
                    x = col * self.sprite_width
                    y = row * self.sprite_height
                    color = (row * 60 % 255, 100 + col * 30 % 155, 50 + (row + col) * 20 % 205)
                    pygame.draw.rect(sprite_sheet, color, (x, y, self.sprite_width, self.sprite_height))
                    pygame.draw.rect(sprite_sheet, BLACK, (x, y, self.sprite_width, self.sprite_height), 1)
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
    
    def update(self, dt, walls, signs, mobs=None):
        # Get keyboard input
        keys = pygame.key.get_pressed()
        move_vec = pygame.Vector2(0, 0)
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_vec.y -= 1
            self.last_direction = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_vec.y += 1
            self.last_direction = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_vec.x -= 1
            self.last_direction = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_vec.x += 1
            self.last_direction = "right"
            
        # Handle stun input
        if keys[pygame.K_p] and self.stun_cooldown <= 0 and mobs:
            self.stun_nearby_mobs(mobs)
            self.stun_cooldown = self.stun_cooldown_time
            
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
        
        # Call parent class update and get old position
        old_pos = super().update(dt)
        
        # Check for collisions with walls
        wall_collisions = pygame.sprite.spritecollide(self, walls, False)
        if wall_collisions:
            # Move back if colliding
            self.pos = old_pos
            self.rect.center = self.pos
        
        # Check if near any signs
        self.can_interact = False
        self.near_sign = None
        for sign in signs:
            if self.rect.colliderect(sign.interact_rect):
                self.can_interact = True
                self.near_sign = sign
                break
        
        # Update stun cooldown
        if self.stun_cooldown > 0:
            self.stun_cooldown -= dt
    
    def stun_nearby_mobs(self, mobs):
        for mob in mobs:
            # distance to mob
            dx = mob.rect.centerx - self.rect.centerx
            dy = mob.rect.centery - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance <= self.stun_radius:
                mob.get_stunned(self.stun_duration)
                # sound effect goes here

class Mob(AnimatedSprite):
    def __init__(self, x, y):
        # Sprite sheet dimensions
        self.sprite_width = 64
        self.sprite_height = 64
        self.cols = 4
        self.rows = 1

        self.chasing = False
        self.chase_distance = 200
        self.chase_speed = 150
        
        # Stun properties
        self.stunned = False
        self.stun_timer = 0
        self.original_speed = 100
        self.stunned_speed = 0
        self.normal_color = (255, 255, 255)  # Default color
        self.stunned_color = (100, 100, 255)  # Blue tint when stunned
        
        # Load sprite sheet and create animation frames
        sprite_sheet = self.load_sprite_sheet("Golem_Run.png", self.cols, self.rows)
        
        # Organize animations
        self.animations = {
            "right": sprite_sheet  # Just use all frames for simple animation
        }
        
        super().__init__((x, y), self.animations["right"])
        self.speed = self.original_speed
        
    def load_sprite_sheet(self, filename, cols, rows):
        try:
            full_path = os.path.join("Sprites", filename)
            sprite_sheet = pygame.image.load(full_path).convert_alpha()
        except:
            # Fallback: create a placeholder sprite sheet
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
    
    def update(self, dt, player, walls):
        # Handle stun timer
        if self.stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
                self.speed = self.original_speed
                # Reset color when stun wears off
                for frame in self.frames:
                    frame.fill(self.normal_color, special_flags=pygame.BLEND_MULT)
        
        # Only move if not stunned
        if not self.stunned:
            if not self.chasing:
                # Check if player is within chase distance
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist < self.chase_distance:
                    self.chasing = True
                    self.speed = self.chase_speed
            else:
                # Get direction to player
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist > 0:
                    # Normalize direction
                    dx /= dist
                    dy /= dist
                    self.direction = pygame.Vector2(dx, dy)
                
                # Check if player is too far away
                if dist > self.chase_distance * 1.5:
                    self.chasing = False
                    self.speed = self.original_speed
        
            # Call parent class update and get old position
            old_pos = super().update(dt)
            
            # Check for collisions with walls
            wall_collisions = pygame.sprite.spritecollide(self, walls, False)
            if wall_collisions:
                # Move back if colliding
                self.pos = old_pos
                self.rect.center = self.pos
            
            # If mob moves out of screen, reset position
            if self.rect.top > SCREEN_HEIGHT + 15 or self.rect.left < -15 or self.rect.right > SCREEN_WIDTH + 15:
                self.rect.x = random.randrange(SCREEN_WIDTH - self.sprite_width)
                self.rect.y = random.randrange(-100, -50)
                self.chasing = False
                self.speed = self.original_speed
    
    def get_stunned(self, duration):
        self.stunned = True
        self.stun_timer = duration
        self.speed = self.stunned_speed
        # Change color to indicate stun status
        for frame in self.frames:
            frame.fill(self.stunned_color, special_flags=pygame.BLEND_MULT)


def main():
    # Show the start screen
    if not show_start_screen():
        return
    
    # Main game loop
    running = True
    while running:
        # Game setup
        all_sprites = pygame.sprite.Group()
        walls = pygame.sprite.Group()
        signs = pygame.sprite.Group()

        # Create walls
        wall_positions = [
            (100, 100, 200, 50),
            (400, 300, 50, 200),
            (700, 200, 200, 50),
            (900, 500, 300, 50)
        ]

        for x, y, w, h in wall_positions:
            wall = Wall(x, y, w, h)
            all_sprites.add(wall)
            walls.add(wall)

        # Create signs with messages
        sign1 = Sign(300, 200, "Welcome to Lone Voyager! Press O to interact with signs.")
        sign2 = Sign(800, 400, "Press P to stun nearby enemies when they chase you!")
        all_sprites.add(sign1)
        all_sprites.add(sign2)
        signs.add(sign1)
        signs.add(sign2)

        player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        all_sprites.add(player)

        # Music setup
        default_music = MusicPlayer("2.Aria of the Soul(P4).mp3")
        chase_music = MusicPlayer("Hollow Knight OST.mp3")
        default_music.play()
        default_music.set_Volume(1.0)
        
        mobs = pygame.sprite.Group()
        for i in range(5):
            mob = Mob(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            all_sprites.add(mob)
            mobs.add(mob)

        # Game play loop
        playing = True
        dt = 0
        chase_music_playing = False
        
        while playing:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        playing = False
                        running = False
                    elif event.key == pygame.K_o and player.can_interact:
                        # Show the sign's message
                        if not show_message_screen(player.near_sign.message):
                            playing = False
                            running = False
            
            # Update
            player.update(dt, walls, signs, mobs)
            
            # Check if any mobs are chasing to switch music
            any_chasing = False
            for mob in mobs:
                mob.update(dt, player, walls)
                if mob.chasing and not mob.stunned:
                    any_chasing = True
            
            # Handle music transitions
            if any_chasing:
                if not chase_music_playing:
                    default_music.stop()
                    chase_music.play()
                    chase_music.set_Volume(1.0)
                    chase_music_playing = True
            else:
                if chase_music_playing:
                    chase_music.stop()
                    default_music.play()
                    chase_music_playing = False
            
            # Check player-mob collisions
            collisions = pygame.sprite.spritecollide(player, mobs, False)
            if collisions:
                playing = False
            
            # Render
            screen.fill(BLACK)
            all_sprites.draw(screen)
            
            # Show interaction prompt if near a sign
            if player.can_interact:
                draw_text(screen, "Press O to read", 24, WHITE, player.rect.centerx, player.rect.top - 20)
            
            # Draw stun cooldown indicator
            if player.stun_cooldown > 0:
                cooldown_width = 200 * (1 - player.stun_cooldown / player.stun_cooldown_time)
                pygame.draw.rect(screen, RED, (10, 10, cooldown_width, 20))
                pygame.draw.rect(screen, WHITE, (10, 10, 200, 20), 2)
                draw_text(screen, "Stun Cooldown", 20, WHITE, 110, 20)
            else:
                draw_text(screen, "Press P to stun nearby enemies", 24, WHITE, SCREEN_WIDTH // 2, 30)
            
            # Flip display
            pygame.display.flip()
            
            # Cap FPS and get delta time
            dt = clock.tick(FPS) / 1000
        
        default_music.stop()
        if chase_music_playing:
            chase_music.stop()
        
        # Show game over screen if not quitting
        if running:
            running = show_game_over_screen()

    pygame.quit()

if __name__ == "__main__":
    main()