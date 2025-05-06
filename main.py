import pygame
import settings

# FOR TOMOROW
# FIRERATE
# AMMO
# HEALTH
# FALL OF PLATFORM
# RESTART SCREEN



def cooldown(time):
    time -= 1/settings.FRAMERATE
    if time <= 0:
        return True, time
    return False,time
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
        
        if self.direction != (0,0):
            self.direction.normalize_ip()

        self.x += self.direction[0]  * self.velocity
        self.y += self.direction[1] * self.velocity


        
        pygame.draw.circle(screen, (69,68,79), (self.x,self.y + 10), 2)
        pygame.draw.circle(screen, (255,255,255), (self.x,self.y), 2)

    def destroy(self):
        pass

class Player:
    def __init__(self, game, x, y):
        self.game = game

        self.rect = pygame.Rect(x,y,8,8)


        self.x = x 
        self.y = y
        self.color = (180,82,82)

        self.vel = pygame.Vector2(0, 0)
        self.move_speed = 2
        

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.ammo = 20

        self.fire_rate = 1/10
        self.time_until_next_shot = 0

    def render(self):
        pygame.draw.circle(self.game.screen, (69,68,79), [self.x, self.y + 2.5], 8) # player shadow
        pygame.draw.circle(self.game.screen, self.color, [self.x, self.y], 8)


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
        if pygame.mouse.get_pressed()[0]:
            self.shoot()

    def shoot(self):
        direction = (pygame.mouse.get_pos()[0] - self.x, pygame.mouse.get_pos()[1] - self.y)
        
        if cooldown(self.time_until_next_shot)[0]:
            self.game.bullets.append(Bullet(self.x, self.y, direction, 5))
            self.time_until_next_shot = self.fire_rate
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
        pygame.draw.rect(self.screen, (69,68,79), pygame.Rect(center[0] - radius , center[1], radius * 2, 700))

        pygame.draw.circle(self.screen, color, center, radius)



    def loop(self):
        while self.running:
            self.screen.fill((134,129,136))

            self.draw_arena()

            for bullet in self.bullets:
                bullet.render(self.screen)

            self.player.render()
            
            

            

            self.player.inputs_shooting()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.player.inputs(event)

            self.player.update()

            pygame.display.flip()
            self.clock.tick(settings.FRAMERATE)

game = Game()

game.loop()