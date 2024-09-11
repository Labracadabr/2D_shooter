import random
import math

import pygame

from polygon_generator import PolyGenerator

# снаряды
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, dmg, png: str, scale: float, facing=1, pierce=1, rotate=0, vel=10, spec='round'):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.png = png
        self.dmg = dmg
        self.rotate = rotate
        self.facing = facing
        self.pierce = pierce
        self.vel = vel
        self.spec = spec
        self.scale = scale
        self.rect = None

    def upd(self, screen):
        if self.spec == 'rocket':
            self.vel *= 1.1
        if self.spec == 'bomb':
            self.vel *= 0.97
        self.y = self.y - (self.vel*self.facing)
        self.rect = screen.blit(self.prep_mask(), (self.x, self.y))

    def prep_mask(self):
        png = pygame.image.load(self.png)
        if self.scale != 1:
            png = pygame.transform.scale_by(png, factor=self.scale)
        if self.rotate:
            png = pygame.transform.rotate(png, angle=self.rotate)
        # mask = pygame.mask.from_surface(png).to_surface()
        return png

    def hit(self, target):
        target.get_damage(self.dmg)
        self.pierce -= 1
        self.vel /= 1.5
        self.dmg /= 1.5


# осколки
class Shrapnel(Projectile):
    def __init__(self, x, y, dmg, direct, size=3, spec='round', pierce=3, duration=20, vel=800):
        super().__init__(x, y, dmg, direct, vel)
        self.direct = direct
        self.duration = duration
        self.size = size
        self.spec = spec
        self.pierce = pierce

    def upd(self, screen):
        self.vel *= 1.1
        # convert angle from degrees to radians
        angle_radians = math.radians(self.direct)
        # calculate movement in x and y directions
        self.x += self.vel * math.cos(angle_radians)
        self.y += -self.vel * math.sin(angle_radians)
        self.rect = pygame.draw.circle(screen, (0, 0, 0, ), (self.x, self.y), self.size)


# враги
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color: tuple, hp=100, vel=1,):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.hp = hp
        self.dmg_color = (225, 220, 220)
        self.norm_color = color
        self.color = color
        self.w = w
        self.h = h
        self.vel = vel
        self.rect = None

    def get_damage(self, damage):
        self.hp -= damage
        self.color = self.dmg_color

    def upd(self, screen):
        # self.rect = pygame.Rect(self.x, self.y, self.radius)
        self.y = self.y + self.vel
        self.rect = pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h, ))
        self.color = self.norm_color

    def create_debris(self) -> list:
        debris = []
        brighter_color = tuple(min(255, i+30) for i in self.norm_color)
        # print(f'{self.norm_color = }')
        # print(f'{brighter_color = }')
        for _ in range(7):
            direction = random.randint(0, 360)
            velocity = random.randint(10, 70)
            debry = Debris(self.x, self.y,
                           polygon=PolyGenerator.random_polygon(num_points=10, scale=self.w / 2),
                           color=brighter_color,
                           direct=direction,
                           vel=velocity,
                           duration=7, )
            debris.append(debry)

        return debris

class Debris(pygame.sprite.Sprite):
    def __init__(self, x, y, polygon, color, direct, vel, duration, ):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.polygon = polygon
        self.color = color
        self.duration = duration
        self.direct = direct
        self.vel = vel
        self.rect = None

    def upd(self, screen):
        self.vel *= 0.7
        # convert angle from degrees to radians
        angle_radians = math.radians(self.direct)

        # calculate movement in x and y directions
        self.x += self.vel * math.cos(angle_radians)
        self.y += -self.vel * math.sin(angle_radians)
        shift_polygon = []
        for point in self.polygon:
            shift_polygon.append(((point[0]+self.x), (point[1]+self.y)))

        self.rect = pygame.draw.polygon(screen, color=self.color, points=shift_polygon)
    def __init__(self, x, y, w, h, color: tuple, hp=100, vel=1,):

# игрок
class Player(object):
    def __init__(self, x, y, w, h, png: str, vel=5, ):
        self.x = x
        self.y = y
        self.png = png
        self.w = w
        self.h = h
        self.vel = vel
        self.rect = None
        self.loaded_png = pygame.image.load(self.png)
        self.scaled_png = pygame.transform.scale(self.loaded_png, (w, h))

    # angle from player to mouse
    def target_angle(self, mouse: tuple):
        dst_x, dst_y = mouse
        degrees = math.degrees(math.atan2(self.y - dst_y, self.x - dst_x))
        if degrees < 0:
            degrees += 360
        return round(degrees, 3)

    def upd(self, screen):
        screen.blit(self.scaled_png, (self.x, self.y))
