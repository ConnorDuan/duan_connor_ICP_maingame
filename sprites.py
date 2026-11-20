import pygame as pg
from pygame.sprite import Sprite
from settings import *
from utils import *
from os import path
from random import randint
import math

vec = pg.math.Vector2

# create player class with Sprite as super Class

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

# this function checks for x and y collision in sequence and sets the position based on collision direction
def collide_with_stuff(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # print("collided with wall from x dir")
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # print("collided with wall from y dir")
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Player(Sprite):
    def __init__(self, game, x, y):
        self.facing_right = True
        self.groups = game.all_sprites
        # also __init__ superclass so Player class has features of superclass
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE, TILESIZE)
        # self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        
        # player motion attributes
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        self.cofric = PLAYER_FRIC
        
        self.hit_rect = PLAYER_HIT_RECT
        self.current_frame = 0
        self.last_update = 0
        self.jumping = False
        self.moving = False
        # self.last_shot = 0
        # self.shoot_delay = 500 
        self.ammo = 1

  
        self.coins = 0
        print("player instance created")
        self.load_images()
        
    def get_keys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
            self.facing_right = False
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC
            self.facing_right = True
            
        # if keys[pg.K_DOWN]:
        #     self.acc.y = PLAYER_ACC
            
        if keys[pg.K_UP] and self.jumping == False:
            self.vel.y = -PLAYER_JUMP_ACC
            
        if keys[pg.K_SPACE]:
            self.pew()
            if self.can_shoot == True:
                if self.ammo > 0:
                    shoot_dir = 15
                    if self.vel.x < 0:
                        shoot_dir = -15
                    PewPew(self.game, self.hit_rect.centerx, self.hit_rect.centery, TILESIZE / 4, TILESIZE / 4, vec(shoot_dir, -2))
                    self.ammo -= 1
                    
        if keys[pg.K_DOWN] and self.jumping == False:
            hits = pg.sprite.spritecollide(self, self.game.all_pews, True)
            if hits:
                self.ammo += 1
        
    def pew(self):
        self.can_shoot = True
        # now = pg.time.get_ticks()
        # if now - self.last_shot > self.shoot_delay:
        #     self.last_shot = now
        #     self.can_shoot = True
        # else:
        #     self.can_shoot = False
            
        
        return self.can_shoot
        
    def load_images(self):
        self.idle_frames = [self.spritesheet.get_image(0,0, TILESIZE,TILESIZE), self.spritesheet.get_image(TILESIZE,0, TILESIZE,TILESIZE)]
        
    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.moving:
            # this determines when to update the screen
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                bottom = self.rect.bottom
                self.image = self.idle_frames[self.current_frame]
                
                # now the player sprite faces the way its walking
                if self.facing_right == False:
                    self.image = pg.transform.flip(self.image, True, False)
                    
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # elif self.moving:
        #     if now - self.last_update > 350:
        #         self.last_update = now
        #         self.current_frame = (self.current_frame + 1) % len(self.moving_frames)
        #         bottom = self.rect.bottom
        #         self.image = self.moving_frames[self.current_frame]
        #         self.rect = self.image.get_rect()
        #         self.rect.bottom = bottom
        # elif self.jumping:
        #     if now - self.last_update > 350:
        #         self.last_update = now
        #         self.current_frame = (self.current_frame + 1) % len(self.jumping_frames)
        #         bottom = self.rect.bottom
        #         self.image = self.jumping_frames[self.current_frame]
        #         self.rect = self.image.get_rect()
        #         self.rect.bottom = bottom

    def update(self):
        
        self.acc = vec(0,20)
        self.get_keys()
        self.animate()
        
        self.acc.x += self.vel.x * self.cofric
        self.vel.x += self.acc.x * self.game.dt
        self.vel.y += self.acc.y * self.game.dt
        
        max_fall_speed = TILESIZE / max(self.game.dt, 0.001)
        self.vel.y = min(self.vel.y, max_fall_speed)
        
        if abs(self.vel.x) < 0.1:
              self.vel.x = 0
        if abs(self.vel.y) < 0.1:
              self.vel.y = 0
        
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * (self.game.dt ** 2)
        
        floor_hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        
        if floor_hits and self.vel.y >= 0:
            self.jumping = False
        elif floor_hits != True:
            self.jumping = True
        
        self.rect.center = self.pos
        
        # self.pos += self.vel * self.game.dt
        
        self.pos += self.vel + 0.5 * self.acc
        
        # if self.vel.y == 0:
        #     self.jumping = False
            
        hits = pg.sprite.spritecollide(self, self.game.all_coins, True)
        if hits:
            self.coins += 1
            self.game.score += 1
            self.game.pickup_snd.play()
            # print(f"I have {self.coins} coins")
            for i in range(20):
                Particle(self.game, hits[0].rect.x, hits[0].rect.y, 1, GOLD)
                hits[0].kill()
            print(str(len(self.game.all_particles)))

        self.hit_rect.centerx = self.pos.x
        collide_with_stuff(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_stuff(self, self.game.all_walls, 'y')
        self.rect.center = self.hit_rect.center
        
        
class PewPew(Sprite):
    def __init__(self, game, x, y, w, h, pew_vel):
        self.groups = game.all_sprites, game.all_pews
        Sprite.__init__(self, self.groups)
        self.game = game
        
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        
        spear_height = int(TILESIZE * 0.75)
        # spear_y_offset = TILESIZE + int(TILESIZE * 2)
        self.image = self.spritesheet.get_image(0, TILESIZE, TILESIZE, spear_height)
        self.image.set_colorkey(BLACK)


        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - TILESIZE / 2
        
        
        self.vel_x = pew_vel.x
        self.vel_y = pew_vel.y
        self.on_ground = False
        self.thrown = False
        self.hit_happened = False

    def update(self):
        
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        if hits and self.hit_happened == False:
            self.hit_happened = True
            for i in range(randint(2, 4)):
                Particle(self.game, self.rect.x, self.rect.y, 0.5, BLCK)
                
            self.on_ground = True
            self.thrown = False
        
        elif hits and self.hit_happened == True:
            self.on_ground = True
            self.thrown = False
        
        else:
            self.hit_happened = False
            self.thrown = True
            self.on_ground = False
            
        

        self.states()
        self.vel_x += self.acc.x * self.game.dt
        self.vel_y += self.acc.y * self.game.dt
        
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        

    def states(self):
        if self.on_ground == True:
            self.acc = vec(0,0)
            self.vel_x = 0
            self.vel_y = 0
            self.image = self.spritesheet.get_image(TILESIZE, TILESIZE, TILESIZE, TILESIZE)
            self.image.set_colorkey(BLACK)
            
        if self.thrown == True:
            self.acc = vec(7,10)
            self.image = self.spritesheet.get_image(0, TILESIZE, TILESIZE, TILESIZE)
            self.image.set_colorkey(BLACK)
            
class Mob(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.image = self.spritesheet.get_image(64,0,TILESIZE, TILESIZE)
        # self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 100
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        self.hit_rect = MOB_HIT_RECT.copy()
        self.current_frame = 0
        self.last_update = 0
        self.jumping = False
        self.moving = False
        self.load_images()
    def load_images(self):
            self.idle_frames = [self.spritesheet.get_image(64,0, TILESIZE,TILESIZE), self.spritesheet.get_image(96,0, TILESIZE,TILESIZE)]
    def animate(self):
            now = pg.time.get_ticks()
            if not self.jumping and not self.moving:
                # this determines when to display the next frame
                if now - self.last_update > 350:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                    bottom = self.rect.bottom
                    self.image = self.idle_frames[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom
            elif self.moving:
                if now - self.last_update > 350:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.moving_frames)
                    bottom = self.rect.bottom
                    self.image = self.moving_frames[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom
                    
    def sight(self, obj):
        my_pos = vec(self.rect.center)
        obj_pos = vec(obj.rect.center)
        sight_line = obj_pos - my_pos
        dist = sight_line.length()
        self.last_seen = vec(0,0)

        if sight_line == (0,0):
            return True
        
        # normalizing stuff gives the simplest version of a vector the direction only
        sight_dir = sight_line.normalize()
        check_rect = pg.Rect(0, 0, 4, 4)
        
        obj_dist = 0
        
        
        while obj_dist < dist:
            current_pos = my_pos + sight_dir * obj_dist
            check_rect.center = (current_pos.x, current_pos.y)
            for wall in self.game.all_walls:
                if check_rect.colliderect(wall.rect):
                    self.last_seen = current_pos - (sight_dir * 4)
                    return False

            obj_dist += 4

        return True        
    
    def behave(self, obj):
        if self.sight(obj) == True:
            self.follow(obj)
            
        # if self.sight(obj) == False:
        #     obj.rect.center = self.last_seen
        #     self.follow(obj)
    
    def follow(self, obj):
        direction = vec(obj.rect.centerx - self.rect.centerx, obj.rect.centery - self.rect.centery)
        if direction.length() > 0:
            direction = direction.normalize()
        self.vel = direction
    
    def update(self):
        self.animate()
        # self.follow(self.game.player)
        self.behave(self.game.player)
        self.pos += self.vel * self.speed * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_stuff(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_stuff(self, self.game.all_walls, 'y')
        # collide_with_stuff(self, self.game.all_mobs, 'x')
        # collide_with_stuff(self, self.game.all_mobs, 'y')
    
        self.rect.center = self.hit_rect.center

class Particle(Sprite):
    def __init__(self, game, x, y, cooldown, color):
        self.groups = game.all_sprites, game.all_particles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE/8, TILESIZE/8))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.vel = vec(randint(60, 80), 0).rotate(randint(0, 360))
        self.pos = vec(x,y)
        self.rect.center = self.pos
        self.speed = 8
        self.cooldown = cooldown
        self.countdown = Cooldown()
        self.countdown.event_time = floor(pg.time.get_ticks()/1000)
        print("I created a particle!")
        print(self.rect.x)
        print(self.rect.y)
    
    def update(self):
        self.countdown.ticking()
        self.pos += self.vel * self.speed * self.game.dt
        if self.countdown.delta > self.cooldown:
            self.kill()
            print(str(len(self.game.all_particles)))
            
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
    
class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0) 
        self.pos = vec(x,y) * TILESIZE
        self.rect.center = self.pos

class FloorTile(Sprite):
    def __init__(self, game, x, y, color):
        self.groups = game.all_sprites, game.all_tiles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0) 
        self.pos = vec(x,y) * TILESIZE
        self.rect.center = self.pos

class Coin(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        pg.draw.circle(self.image, GOLD, (TILESIZE/2, TILESIZE/2), TILESIZE/2)
        # pg.draw.ellipse(self.image, GOLD, (TILESIZE/2, TILESIZE/2), TILESIZE/2)
        self.image.set_colorkey(BLCK)
        # self.image.fill(GOLD)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0) 
        self.pos = vec(x,y) * TILESIZE
        self.rect.center = self.pos