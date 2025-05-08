import pygame
import settings
import math 
import sys

# Ideas
# Exploding bullets damage the arena

# Reminders
# Instead of suddenly disapearing make the health bar fade away - Visual improvement
# Need to implement reload - Core Gameplay
# Delete bullets that are offscreen - Perfomance improvement
# Need to implement the theme  - Unstable
# Organize the structure of the project - Only if there's time left 

# FOR TOMOROW - Closes Basic gameplay loop
# RESTART SCREEN


# Utils
# def draw_text(text, font, color, surface, x ,y):
#     text_obj = font.render(text, 1, color)
#     text_rect = text_obj.get_rect()
#     text_rect.topleft = (x, y)
#     surface.blit(text_obj, text_rect)

def cooldown(time):
    time -= 1/settings.FRAMERATE
    if time <= 0:
        return True, time
    return False,time

# font = pygame.font.SysFont("sdglitchdemoregular", 20)




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
    def __init__(self, velocity, duration):
        self.velocity = velocity
        self.duration = duration

class Bullet:
    def __init__(self, x, y, direction, velocity):
        self.damage = 5
        
        self.velocity = 2
        self.direction = pygame.Vector2(direction[0], direction[1])

        self.x = x
        self.y = y

    def render(self, surface):
        pygame.draw.circle(surface, (69,68,79), (self.x,self.y + 10), 2)
        pygame.draw.circle(surface, (255,255,255), (self.x,self.y), 2)

    def update(self):
        if self.direction != (0,0):
            self.direction.normalize_ip()

        self.x += self.direction[0]  * self.velocity
        self.y += self.direction[1] * self.velocity

    def destroy(self):
        pass

class Player:
    def __init__(self, game, x, y):
        # Reference to the game (mostly used to reference the surface needed to display the player)
        self.game = game
        
        # Player render?
        self.rect = pygame.Rect(x,y,8,8)
        self.x = x 
        self.y = y
        self.color = (180,82,82)


        # Movement
        self.vel = pygame.Vector2(0, 0)
        self.move_speed = 2

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Attacking
        self.ammo = 20
        self.fire_rate = 1/10
        self.time_until_next_shot = 0

        # Health
        self.max_health = 30
        self.health = self.max_health
        self.health_rect = pygame.Rect(self.x - 15, self.y - 15, self.health, 2)

        self.show_health = False
        self.show_health_time = 5
        self.time_until_health_stops_showing = self.show_health_time

    def render(self):
        # Shadow
        pygame.draw.circle(self.game.surface, (69,68,79), [self.x, self.y + 2.5], 8) 
        # Player
        pygame.draw.circle(self.game.surface, self.color, [self.x, self.y], 8)

        if self.show_health:
            # Health bar
            pygame.draw.rect(self.game.surface, (69,68,79), pygame.Rect(self.health_rect.x, self.health_rect.y, self.max_health, 2))
            pygame.draw.rect(self.game.surface, (255,255,255), self.health_rect)

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
            self.game.bullets.append(Bullet(self.x, self.y, direction, 5))
            self.time_until_next_shot = self.fire_rate
            self.ammo -= 1
        else: 
            self.time_until_next_shot = cooldown(self.time_until_next_shot)[1]

    def update(self):
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

       
        if self.show_health:
             # Update healthbar position
            self.health_rect.x = self.x - 15
            self.health_rect.y = self.y - 15

            if cooldown(self.time_until_health_stops_showing)[0]:
                self.show_health = False
                self.time_until_health_stops_showing = self.show_health_time
            else: 
                self.time_until_health_stops_showing = cooldown(self.time_until_health_stops_showing)[1]
        
        # Slowly heal player - improve later
        self.heal(.025)

        if self.health <= 0:
            self.die()


    def take_damage(self, amount):
        self.health -= amount
        self.health = pygame.math.clamp( self.health, 0 , self.max_health) 
        self.health_rect.width = self.health

        self.show_health = True
        self.time_until_health_stops_showing = self.show_health_time

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

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Bullet Hell - Unstable")
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.surface = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA) # Surface used for trasnparency

        self.clock = pygame.time.Clock()
        self.running = True
        
        # UI
        self.ui = UI(self)
        self.current_scene = 'Main Menu'
        self.scenes = {
            'Main Menu': self.main_menu,
            'Game': self.game,
            'Settings': self.settings,
            'Restart': self.restart_menu
        }

        self.player = Player(self, settings.WIDTH/2, settings.HEIGHT/2)
        self.mx, self.my = pygame.mouse.get_pos()

        self.bullets = []

        self.arena_center = (350,400)
        self.arena_radius = 250

        self.click = False

    def scene_manager(self):
        while self.running:
            # Clear the surface at the start of each frame
            self.surface.fill((0, 0, 0, 0))  # Clear with transparent
            
            # Handle scene transition
            scene_method = self.scenes.get(self.current_scene, self.main_menu)
            scene_method()
            
            # Blit surface to screen and flip display
            self.screen.blit(self.surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(settings.FRAMERATE)


    def draw_arena(self, color=(100,99,101) ):
        # Pillar / shadow
        pygame.draw.rect(self.surface, (69,68,79), pygame.Rect(self.arena_center[0] - self.arena_radius , self.arena_center[1], self.arena_radius * 2, 700))
        # Arena
        pygame.draw.circle(self.surface, color, self.arena_center, self.arena_radius)

    def settings(self):
        pass

    def main_menu(self):
        self.surface.fill((0, 0, 0, 255))
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
        self.surface.fill((0, 0, 0, 255))
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
        self.player = Player(self, settings.WIDTH/2, settings.HEIGHT/2)
        self.bullets = []

    def game(self):
        # Clear screen and surface
        self.screen.fill((134,129,136))
        self.surface.fill((0, 0, 0, 0))  # Clear with transparent
        
        # Game rendering
        self.draw_arena()
        for bullet in self.bullets:
            bullet.render(self.surface)
        self.player.render()
        
        # Handle events
        self.player.inputs_shooting()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.player.inputs(event)
        
        # Game updates
        for bullet in self.bullets[:]:  # Iterate over a copy to allow removal
            bullet.update()
            # Remove bullets off-screen (performance improvement)
            if (bullet.x < 0 or bullet.x > settings.WIDTH or 
                bullet.y < 0 or bullet.y > settings.HEIGHT):
                self.bullets.remove(bullet)
        
        self.player.update()

game = Game()

game.scene_manager()