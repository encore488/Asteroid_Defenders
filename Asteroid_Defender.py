import pygame, os, time, random
from pygame import mixer

pygame.init()
pygame.font.init()


s_width = 1000
s_height = 700
screen = pygame.display.set_mode((s_width, s_height))


pygame.display.set_caption("Stop The Asteroids!")

# Meteor images
meteor1 = pygame.transform.scale(pygame.image.load("meteor1.png"), (180,180)).convert_alpha()
meteor2_crooked = pygame.transform.scale(pygame.image.load("meteor2-removebg-preview.png"), (100,100)).convert_alpha()
meteor2 = pygame.transform.rotate(meteor2_crooked, -45)
meteor3 = pygame.transform.scale(meteor2, (60, 60))


# Boss Image
#boss_image = pygame.image.load("purple_fighter_jet.jpg")

# Background
backg_img = pygame.transform.scale(pygame.image.load("EarthHorizon.jpg"), (s_width, s_height))

# Player 1
bolt_img_big = pygame.transform.rotate(pygame.image.load("BlasterBolt-removebg-preview.png"), -90)
bolt_img = pygame.transform.scale(bolt_img_big, (200, 80))
player1_Image = pygame.transform.scale(pygame.image.load("fightJet-removebg-preview.png"), (80,80)).convert_alpha()
player_vel = 5


class Laser():
    def __init__(self, x, y, img):
        self.x=x
        self.y=y
        self.img=img
        self.mask=pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y>=0)

    def collision(self, obj):
        return collide(obj, self)


class Ship:
    COOLDOWN = 20
    def __init__(self,x,y,health=100):
        self.x=x
        self.y=y
        self.health=health
        self.ship_img = None
        self.laser_img = None
        self.lasers=[]
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(s_height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -=10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-60, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Asteroid(Ship):
    SIZE_MAP = {
        "Big":(300, meteor1),
        "Medium": (200, meteor2),
        "Small":(100, meteor3)
        }
    def __init__(self, x,y,size):
        super().__init__(x,y)
        self.health, self.ship_img = self.SIZE_MAP[size]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.ship_img = player1_Image
        self.laser_img = bolt_img
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(s_height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        #obj.health -=10
                        if laser in self.lasers:
                            self.lasers.remove(laser)

        def draw(self, screen):
            super().draw(screen)
            self.healthbar(screen)

        def healthbar(self, screen):
            pygame.draw.rect(screen, (255,0,0), (self.x, self.y + self.ship_img.get_height()+10, self.ship_img.get_width(), 10))
            pygame.draw.rect(screen, (0,255,0), (self.x, self.y + self.ship_img.get_height()+10, self.ship_img.get_width() * (self.health/self.max_health), 10))


# Sound
#mixer.music.load('Arcane_Battle.ogg.mp3')
#mixer.music.play(-1)

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    #game loop
    running = True
    FPS = 60
    clock = pygame.time.Clock()

    level = 0
    lives = 10
    main_font = pygame.font.SysFont("arial", 20)
    lost_font = pygame.font.SysFont("arial", 30)

    player = Player(300,650)
    player_vel = 5
    laser_vel = 8

    enemies = []
    wave_length = 5

    lost = False
    lost_count = 0

    def redraw_window():
        #Draw background image
        screen.blit(backg_img, (0,0))
        #Draw lives and level labels
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        screen.blit(lives_label, (880, 8))
        screen.blit(level_label, (880, 35))
        
        for enemy in enemies:
            enemy.draw(screen)

            #draw main player
        player.draw(screen)

        if lost:
            lost_label = lost_font.render("You Have Lost. Earth Cannot Take So Many Asteroids", 1, (255,255,255))
            screen.blit(lost_label, (s_width/2 - lost_label.get_width()/2, 350))

        pygame.display.update()


    while running:
        clock.tick(FPS)

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

            if lost_count > FPS*5:
                running = False
            else:
                redraw_window()
                continue

        if len(enemies) ==0:
            level+=1
            wave_length += 3
            for i in range(wave_length):
                enemy = Asteroid(random.randrange(50, s_width-100), random.randrange(-1500, -100), random.choice(["Big","Medium","Small"]))
                enemies.append(enemy)



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel+player.get_width() < s_width:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel+player.get_height() < s_height:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(0.8)
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > s_height:
                lives -= 1
                enemies.remove(enemy)


        player.move_lasers(-laser_vel, enemies)

        redraw_window()

def main_menu():
    title_font = pygame.font.SysFont("arial", 70)
    run = True
    while run:
        screen.blit(backg_img, (0,0))
        title_label = title_font.render("Press the Mouse to Start", 1, (255, 255, 255))
        screen.blit(title_label, (s_width/2 - title_label.get_width()/2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()