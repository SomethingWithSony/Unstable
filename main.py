import pygame
import settings
import colors
import math 
import random
import os

# Ideas
# Exploding bullets damage the arena



   

# Reminders
# Instead of suddenly disapearing make the health bar fade away - Visual improvement
# Need to implement reload - Core Gameplay
# Need to implement the theme  - Unstable
# Organize the structure of the project - Only if there's time left 

# FOR TODAY - Closes Basic gameplay loop
# Enemies & Playtesting

# Enemy types
# Normal type 2 , runs after you and explodes when near
# Ranged 1 Shot 
# Diferent sizes != speed , Big big damage slow, small small damage , fast, normal normal normal




# FOR TOMORROW 
# Boss



# Utils
def cooldown(time):
    time -= 1/settings.FRAMERATE
    if time <= 0:
        return True, time
    return False,time





# Classes
class UI:
    def __init__(self, game):
        self.game = game
        self.font_cache = {}
        
    def get_font(self, font_name, size):
        key = (font_name, size)
        if key not in self.font_cache:
            self.font_cache[key] = pygame.font.SysFont(font_name, size)
        return self.font_cache[key]
    
    def draw_text(self, text, font_name, size, color, x, y):
        font = self.get_font(font_name, size)
        text_surface = font.render(text, True, color)
        self.game.surface.blit(text_surface, (x, y))
        return text_surface.get_rect(topleft=(x, y))
    
    def draw_button(self, text, font_name, size, color, x, y, padding=10):
        text_rect = self.draw_text(text, font_name, size, color, x, y)
        button_rect = text_rect.inflate(padding*2, padding*2)
        pygame.draw.rect(self.game.surface, color, button_rect, 2)
        return button_rect

# Implement after the core gameplay is finished
class Particle:
    def __init__(self, x, y,velocity , duration):
        self.velocity = velocity
        self.duration = duration

class GameObject:
    def __init__(self, x: float, y: float, radius: float):
        self.x = x
        self.y = y
        self.radius = radius
        self.is_active = True
    
    def update(self):
        pass
    
    def render(self):
        pass
    
    def collides_with(self, other: 'GameObject') -> bool:
        # Check circle collision with another game object
        if not self.is_active or not other.is_active:
            return False
            
        dx = self.x - other.x
        dy = self.y - other.y
        distance_squared = dx*dx + dy*dy
        radius_sum = self.radius + other.radius
        return distance_squared < radius_sum*radius_sum
    
class Bullet(GameObject):
    def __init__(self, x, y, direction, velocity, damage):
        super().__init__(x, y, 5)
        self.damage = damage
        self.velocity = velocity
        self.direction = pygame.Vector2(direction[0], direction[1])

    def render(self, surface, offset=(0,0)):
        pygame.draw.circle(surface, colors.ENTITY_SHADOW, (self.x + offset[0],self.y + offset[1] + 10), 2)
        pygame.draw.circle(surface, colors.PLAYER_BULLET, (self.x + offset[0], self.y + offset[1]), 2)

    def update(self):
        if self.direction != (0,0):
            self.direction.normalize_ip()

        self.x += self.direction[0]  * self.velocity
        self.y += self.direction[1] * self.velocity

    def destroy(self):
        pass

class PhysicsEntity(GameObject):
    def __init__(self, game, x, y,radius):
        super().__init__(x, y, radius)
        self.game = game
        self.surface = game.surface

        self.knockback_dx = 0
        self.knockback_dy = 0
        self.knockback_frames = 0

    def apply_knockback(self, dx: float, dy: float, force: float = 10, duration: int = 10):
        self.knockback_dx = dx * force
        self.knockback_dy = dy * force
        self.knockback_frames = duration

    def handle_knockback(self):
        if self.knockback_frames > 0:
            self.x += self.knockback_dx
            self.y += self.knockback_dy
            self.knockback_frames -= 1
            self.knockback_dx *= 0.9  # Reduce knockback each frame
            self.knockback_dy *= 0.9
            return  True
        
        return False

class Player(PhysicsEntity):
    def __init__(self,game, x, y, color):
        super().__init__(game,x, y, 20)

        # Player render?
        self.rect = pygame.Rect(x,y,8,8)
        self.color = color

        # Movement
        self.vel = pygame.Vector2(0, 0)
        self.move_speed = 2

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Attacking
        self.ammo = 2000
        self.fire_rate = 1/10
        self.time_until_next_shot = 0

        # Health
        self.max_health = 30
        self.health = self.max_health
        self.health_rect = pygame.Rect(self.x - 15, self.y - 15, self.health, 2)
  
        self.health_duration = 3 * settings.FRAMERATE
        self.health_frames = 0
        self.health_alpha = 255
        self.health_shadow_alpha = 255


    def render(self, offset=(0, 0)):
        # Shadow   
        pygame.draw.circle(self.surface, colors.ENTITY_SHADOW, [self.x + offset[0], self.y + offset[1] + 5], 8) 

        if self.knockback_frames > 0 and self.knockback_frames % 4 < 2:
            color = colors.DAMAGE  # Flash 
        else:
            color = self.color
            
        # Player
        pygame.draw.circle(self.surface, color, [self.x + offset[0], self.y + offset[1]], 8)

        if self.health_frames > 0:
            self.health_frames -= 1
            # Health bar
            pygame.draw.rect(self.surface, (69,68,79, self.health_shadow_alpha), pygame.Rect(self.health_rect.x + offset[0], self.health_rect.y + offset[1], self.max_health, 2))
            pygame.draw.rect(self.surface, (255,255,255, self.health_alpha), self.health_rect)

    def inputs(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.left_pressed = True
            if event.key == pygame.K_d:
                self.right_pressed = True

            if event.key == pygame.K_w:
                self.up_pressed = True
            if event.key == pygame.K_s:
                self.down_pressed = True

            if event.key == pygame.K_t:
                self.take_damage(5)

            if event.key == pygame.K_h:
                self.heal(5)
                print(self.game.bullets)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.left_pressed = False
            if event.key == pygame.K_d:
                self.right_pressed = False

            if event.key == pygame.K_w:
                self.up_pressed = False
            if event.key == pygame.K_s:
                self.down_pressed = False

    def inputs_shooting(self):
        if pygame.mouse.get_pressed()[0] and self.ammo > 0:
            self.shoot()
            
        if self.ammo == 0 :
            # print("Out of ammo")
            # Reload or something
            pass

    def shoot(self):
        direction = (pygame.mouse.get_pos()[0] - self.x, pygame.mouse.get_pos()[1] - self.y)
        
        if cooldown(self.time_until_next_shot)[0]:
            self.game.shot_sfx.play()
            self.game.bullets.append(Bullet(self.x, self.y, direction, 5, 5))
            self.time_until_next_shot = self.fire_rate
            self.ammo -= 1
        else: 
            self.time_until_next_shot = cooldown(self.time_until_next_shot)[1]

    def update(self):
        self.handle_knockback()
        self.detect_out_of_arena()

        self.vel = pygame.Vector2(0, 0)
        if self.left_pressed and not self.right_pressed:
            self.vel[0] = -self.move_speed
        if self.right_pressed and not self.left_pressed:
            self.vel[0] = self.move_speed
        if self.up_pressed and not self.down_pressed:
            self.vel[1] = -self.move_speed
        if self.down_pressed and not self.up_pressed:
            self.vel[1] = self.move_speed
            
        if self.vel != (0,0):
            self.vel.normalize_ip()
            
        self.x += int(self.vel[0] * self.move_speed)
        self.y += int(self.vel[1] * self.move_speed)

       
        if self.health_frames > 0:
             # Update healthbar position
            self.health_rect.x = self.x - 15
            self.health_rect.y = self.y - 15

            
            if self.health_frames < 60:
                self.health_alpha = max(0, self.health_alpha - 6.5)
                self.health_shadow_alpha = max(0, self.health_shadow_alpha - 2.7)
        
        self.heal(.025)

        if self.health <= 0:
            self.die()

    def take_damage(self, amount):
        self.game.hit_sfx[random.randint(0, len(self.game.hit_sfx) - 1)].play()
        self.health -= amount
        self.health = pygame.math.clamp( self.health, 0 , self.max_health) 
        self.health_rect.width = self.health

        self.health_frames = self.health_duration
        self.health_alpha = 255 
        self.health_shadow_alpha = 255 

    def heal(self, amount):
        self.health += amount
        self.health = pygame.math.clamp( self.health, 0 , self.max_health) 
        self.health_rect.width = self.health

    def detect_out_of_arena(self):
        # Distance between the center of the arena and the player
        distance = math.sqrt( (self.x - self.game.arena_center[0])**2 + (self.y - self.game.arena_center[1])**2)
        
        offset = 7
        # If the distance between the player and the center of the arena is > the player is outside the arena
        if distance  <= self.game.arena_radius + offset:
            pass
        else:
            print("outside")
            self.die()

    def die(self):
        # Explode particle and restart_menu screen
        # or
        # Animate player falling - a simple layer system may be needed
        # Activate resttart screen
        self.game.current_scene = "Restart"

class Enemy(PhysicsEntity):
    def __init__(self,game, health, move_speed, fire_rate, x, y, color):
        super().__init__(game,x, y, 5)
        self.surface = game.surface
        self.player = game.player
        self.health = health
        self.move_speed = 1
        self.fire_rate = fire_rate

        self.color = color

        # self.spinning_rect = SpinningRect(self.x, self.y - 13, 30, 2, colors.ENEMY_STD_SEC)
        # self.spinning_rect_shadow = SpinningRect(self.x, self.y , 30, 2, colors.ENTITY_SHADOW)

    def avoid_other_enemies(self):
        separation_radius = 32  # Distance at which separation applies
        separation_force = 0.5  # Strength of separation
        
        total_x, total_y, count = 0, 0, 0
        
        for enemy in self.game.enemies:
            if enemy != self:
                dx = self.x - enemy.x
                dy = self.y - enemy.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < separation_radius and dist > 0:
                    total_x += dx/dist
                    total_y += dy/dist
                    count += 1
        
        if count > 0:
            # Normalize and apply separation force
            self.x += (total_x/count) * separation_force
            self.y += (total_y/count) * separation_force

    def move_towards_player(self):
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            # Stop at a certain distance from player
            min_distance_from_player = 16
            if dist > min_distance_from_player:
                self.x += (dx/dist) * self.move_speed
                self.y += (dy/dist) * self.move_speed
            else:
                # Move around the player in a circle
                angle = math.atan2(dy, dx)
                self.x = self.player.x - math.cos(angle) * min_distance_from_player
                self.y = self.player.y - math.sin(angle) * min_distance_from_player

    def render(self, offset=(0, 0)):
        # Shadow
        # self.spinning_rect_shadow.render(self.surface)
        pygame.draw.circle(self.surface, colors.ENTITY_SHADOW, [self.x + offset[0], self.y + offset[1] + 3], 8)

        # Enemy
        # Flash When hit
        if self.knockback_frames > 0 and self.knockback_frames % 4 < 2:
            color = colors.DAMAGE  # Flash 
        else:
            color = self.color

        pygame.draw.circle(self.surface, color, [self.x + offset[0], self.y + offset[1]], 8)

        # pygame.draw.rect(self.surface, colors.ENEMY_STD_SEC, pygame.Rect(self.x + offset[0] - 1 , self.y + offset[1] - 13, 2, 10)) 

        # Helicopter
        # self.spinning_rect.render(self.surface)
 
    def update(self):
        # Handle knockback first
        shake = self.handle_knockback()

        # self.spinning_rect_shadow.update()
        # self.spinning_rect.update()

        # Update spinning part positioning
        # self.spinning_rect.x = self.x
        # self.spinning_rect.y = self.y - 13
        # self.spinning_rect_shadow.x = self.x + 5
        # self.spinning_rect_shadow.y = self.y + 3

        if shake:
            return
   
        self.move_towards_player()
        self.avoid_other_enemies()

class SpinningRect:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.angle = 0
        self.rotation_speed = 6  # Degrees per frame
        
        # Create the original surface with the rectangle
        self.original_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(self.original_surface, color, (0, 0, width, height))
        
    def update(self):
        self.angle = (self.angle + self.rotation_speed) % 360
        
    def render(self, surface):
        # Rotate the original surface
        rotated_surface = pygame.transform.rotate(self.original_surface, self.angle)
        
        # Get the rect of the rotated surface and set its center
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
        
        # Draw the rotated surface
        surface.blit(rotated_surface, rotated_rect)

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

        pygame.display.set_caption("Bullet Hell - Unstable")
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.surface = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA) # Surface used for trasnparency

        pygame.mouse.set_visible(False)
        self.cursor_img = pygame.image.load(os.path.join('assets', 'dot.png'))
        self.cursor_img_rect = self.cursor_img.get_rect()

        self.clock = pygame.time.Clock()
        self.running = True
        
        # UI
        self.score = 0
        self.ui = UI(self)
        self.current_scene = 'Main Menu'
        self.scenes = {
            'Main Menu': self.main_menu,
            'Game': self.game,
            'Settings': self.settings,
            'Restart': self.restart_menu
        }

        self.player = Player(self, settings.WIDTH/2, settings.HEIGHT/2, colors.PLAYER)
        self.mx, self.my = pygame.mouse.get_pos()

        self.bullets = []
         
        self.enemies = [ Enemy(self, 10, 5, 5, random.randint(150, 550), random.randint(150, 550), colors.ENEMY_STD) for i in range(10) ]

        self.arena_center = (350,400)
        self.arena_radius = 250

        self.click = False
        self.screen_shake = 0

        # Sounds
        self.hit_sfx = [self.load_sfx("hit"),self.load_sfx("hit2"),self.load_sfx("hit3"),self.load_sfx("hit4"),self.load_sfx("hit5")]
        self.death_sfx = [self.load_sfx("death"),self.load_sfx("death2"),self.load_sfx("death3"),self.load_sfx("death4"),self.load_sfx("death5")]
        self.shot_sfx = pygame.mixer.Sound(os.path.join("assets", "shot.wav"))

    def load_sfx(self, name):
        return pygame.mixer.Sound(os.path.join("assets", f"{name}.wav"))

    def apply_screen_shake(self, intensity: int = 5, duration: int = 10):
        self.screen_shake = max(self.screen_shake, intensity)
        self.shake_duration = duration

    def scene_manager(self):
        while self.running:
            
            # Clear the surface at the start of each frame
            self.surface.fill((0, 0, 0, 0))  # Clear with transparent

            


            # Handle scene transition
            scene_method = self.scenes.get(self.current_scene, self.main_menu)
            scene_method()
            
            # Blit surface to screen and flip display
            self.screen.blit(self.surface, (0, 0))
            self.cursor_img_rect.center = pygame.mouse.get_pos()  
            self.screen.blit(self.cursor_img, self.cursor_img_rect) 
            pygame.display.flip()
            self.clock.tick(settings.FRAMERATE)

    def draw_arena(self):
        # Pillar / shadow
        pygame.draw.rect(self.surface, colors.SHADOW_ARENA, pygame.Rect(self.arena_center[0] - self.arena_radius , self.arena_center[1], self.arena_radius * 2, 700))
        # Arena
        pygame.draw.circle(self.surface, colors.ARENA_BASE, self.arena_center, self.arena_radius )

    def settings(self):
        pass

    def main_menu(self):
        self.surface.fill(colors.BACKGROUND)
        # Clear click state at start
        self.click = False
        
        # Draw UI elements
        self.ui.draw_text("UN", "sdglitchdemoregular", 150, (255,255,255), 290, 70)
        self.ui.draw_text("STABLE", "sdglitchdemoregular", 150, (255,255,255), 180, 200)
        
        # Draw buttons and check clicks
        play = self.ui.draw_button("PLAY", "sdglitchdemoregular", 50, (255,255,255), 315, 380)
        settings = self.ui.draw_button("SETTINGS", "sdglitchdemoregular", 50, (255,255,255), 280, 440)
        quit_ = self.ui.draw_button("QUIT", "sdglitchdemoregular", 50, (255,255,255), 320, 500)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.click = True
        
        # Handle button clicks
        if self.click:
            if play.collidepoint(pygame.mouse.get_pos()):
                self.current_scene = "Game"
                self.reset_game()  
            elif settings.collidepoint(pygame.mouse.get_pos()):
                self.current_scene = "Settings"
            elif quit_.collidepoint(pygame.mouse.get_pos()):
                self.running = False

    def restart_menu(self):
        self.surface.fill(colors.BACKGROUND)
        # Clear click state at start
        self.click = False

        self.ui.draw_text("GAME OVER", "sdglitchdemoregular", 150, (255,255,255),  75, 70)
        
        restart = self.ui.draw_button("RESTART", "sdglitchdemoregular", 50, (255,255,255), 290, 380)
        quit_ = self.ui.draw_button("QUIT", "sdglitchdemoregular", 50, (255,255,255), 320, 440)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.click = True
        
        # Handle button clicks
        if self.click:
            if restart.collidepoint(pygame.mouse.get_pos()):
                self.current_scene = "Game"
                self.reset_game()  
            elif quit_.collidepoint(pygame.mouse.get_pos()):
                self.running = False

    def reset_game(self):
        # Reset all game objects when starting a new game
        self.player = Player(self, settings.WIDTH/2, settings.HEIGHT/2, colors.PLAYER)
        self.bullets = []
        self.enemies = [ Enemy(self, 10, 5, 5, random.randint(150, 550), random.randint(150, 550), colors.ENEMY_STD) for i in range(10) ]


    def game(self):
        # Clear screen and surface
        self.screen.fill(colors.BACKGROUND)
        self.surface.fill((0, 0, 0, 0))  # Clear with transparent
        
        shake_offset = (
            (random.random() * 2 - 1) * self.screen_shake,
            (random.random() * 2 - 1) * self.screen_shake
        ) if self.screen_shake > 0 else (0, 0)

        # Game rendering
        self.draw_arena()
        for bullet in self.bullets:
            bullet.render(self.surface, shake_offset)

        for enemy in self.enemies:
            enemy.render(shake_offset)

        self.player.render(shake_offset)

        # Reduce screen shake
        if self.screen_shake > 0:
            self.screen_shake *= 0.9
            if self.screen_shake < 0.1:
                self.screen_shake = 0

        
        # Handle events
        self.player.inputs_shooting()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.player.inputs(event)
        
        # Game updates
        for bullet in self.bullets[:]:  # Iterate over a copy to allow removal
            if not bullet.is_active:
                self.bullets.remove(bullet)
                continue

            if bullet.x < 0 or bullet.x > settings.WIDTH or bullet.y < 0 or bullet.y > settings.HEIGHT:
                bullet.is_active = False

            # if self.player.collides_with(bullet):
            #     print("Player hit by enemy wtih bullet!")
            
            for enemy in self.enemies[:]:
                if enemy.is_active and bullet.collides_with(enemy):
                    self.hit_sfx[random.randint(0, len(self.hit_sfx) - 1)].play()


                    knockback_dx = enemy.x - bullet.x
                    knockback_dy = enemy.y - bullet.y
                    dist = math.sqrt(knockback_dx**2 + knockback_dy**2)
                    
                    if dist > 0:
                        # Normalize and apply knockback
                        enemy.apply_knockback(knockback_dx/dist, knockback_dy/dist, .2, 5)
                        

                    enemy.health -= bullet.damage
                    bullet.is_active = False
                    if enemy.health <= 0:
                        self.death_sfx[random.randint(0, len(self.death_sfx) - 1)].play()
                        self.apply_screen_shake(10, 15)
                        enemy.is_active = False
                        self.score += 10
                    break
            # Remove bullets off-screen (performance improvement)
            if (bullet.x < 0 or bullet.x > settings.WIDTH or 
                bullet.y < 0 or bullet.y > settings.HEIGHT):
                self.bullets.remove(bullet)

            bullet.update()
            
        for enemy in self.enemies[:]:
            if not enemy.is_active:
                self.enemies.remove(enemy)

            if self.player.collides_with(enemy):
                print("Player hit by enemy!")
                knockback_dx =  self.player.x - enemy.x 
                knockback_dy = self.player.y - enemy.y 

                dist = math.sqrt(knockback_dx**2 + knockback_dy**2)
                
                if dist > 0:
                    # Normalize and apply knockback
                    self.player.apply_knockback(knockback_dx/dist, knockback_dy/dist, 5, 10)
                    self.player.take_damage(5)
                
            
            
            enemy.update()
        
        self.player.update()

game = Game()

game.scene_manager()