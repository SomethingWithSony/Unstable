import pygame
import settings

# Ideas
# Exploding bullets damage the arena

# Reminders
# Instead of suddenly disapearing make the health bar fade away - Visual improvement
# Need to implement reload - Core Gameplay
# Delete bullets that are offscreen - Perfomance improvement
# Need to implement the theme  - Unstable
# Organize the structure of the project - Only if there's time left 

# FOR TOMOROW - Closes Basic gameplay loop
# FALL OF PLATFORM
# RESTART SCREEN


def cooldown(time):
    time -= 1/settings.FRAMERATE
    if time <= 0:
        return True, time
    return False,time

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

    def render(self, screen):
        pygame.draw.circle(screen, (69,68,79), (self.x,self.y + 10), 2)
        pygame.draw.circle(screen, (255,255,255), (self.x,self.y), 2)

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
        self.health = 25
        self.health_rect = pygame.Rect(self.x - 15, self.y - 15, self.health, 2)

        self.show_health = True
        self.show_health_time = 5
        self.time_until_health_stops_showing = self.show_health_time

    def render(self):
        # Shadow
        pygame.draw.circle(self.game.screen, (69,68,79), [self.x, self.y + 2.5], 8) 
        # Player
        pygame.draw.circle(self.game.screen, self.color, [self.x, self.y], 8)

        if self.show_health:
            # Health bar
            pygame.draw.rect(self.game.screen, (69,68,79), pygame.Rect(self.health_rect.x, self.health_rect.y, self.max_health, 2))
            pygame.draw.rect(self.game.screen, (255,255,255), self.health_rect)

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
            print("Out of ammo")

    def shoot(self):
        direction = (pygame.mouse.get_pos()[0] - self.x, pygame.mouse.get_pos()[1] - self.y)
        
        if cooldown(self.time_until_next_shot)[0]:
            self.game.bullets.append(Bullet(self.x, self.y, direction, 5))
            self.time_until_next_shot = self.fire_rate
            self.ammo -= 1
        else: 
            self.time_until_next_shot = cooldown(self.time_until_next_shot)[1]

    def update(self):
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

    def take_damage(self, amount):
        self.heatlh = pygame.math.clamp( self.health  - amount, 0 , self.max_health) 

    def heal(self, amount):
        self.heatlh = pygame.math.clamp( self.health  + amount, 0 , self.max_health) 
        
    def die(self):
        # die
        pass

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Bullet Hell - Unstable")
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))

        self.clock = pygame.time.Clock()
        self.running = True

        self.player = Player(self, settings.WIDTH/2, settings.HEIGHT/2)

        self.bullets = []
        

    def draw_arena(self, color=(100,99,101), center=(350,400), radius=250):
        # Pillar / shadow
        pygame.draw.rect(self.screen, (69,68,79), pygame.Rect(center[0] - radius , center[1], radius * 2, 700))

        # Arena
        pygame.draw.circle(self.screen, color, center, radius)



    def loop(self):
        while self.running:
            self.screen.fill((134,129,136))

            # Renders
            self.draw_arena()
            for bullet in self.bullets:
                bullet.render(self.screen)
            self.player.render()
            
            # Inputs
            self.player.inputs_shooting()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.player.inputs(event)

            # Updates
            for bullet in self.bullets:
                bullet.update()
            self.player.update()
            

            pygame.display.flip()
            self.clock.tick(settings.FRAMERATE)

game = Game()

game.loop()