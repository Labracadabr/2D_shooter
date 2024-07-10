from random import randint as rndm
from random import random, choice
import pygame
from objects import Player, Projectile, Enemy, Shrapnel

# colors
RED = (255, 0, 0,)
GREEN = (0, 255, 0,)
BLUE = (0, 0, 255,)
BLACK = (0, 0, 0,)
YELLOW = (255, 255, 0,)
GREY = (100, 100, 100,)
WHITE = (255, 255, 255,)
BG = (40, 30, 30,)

# initialize
pygame.init()
SCREEN_SIZE = (1200, 800)
screen = pygame.display.set_mode(SCREEN_SIZE)
text_font = pygame.font.SysFont('Arial', 25)
clock = pygame.time.Clock()
enemy_hp_mult = 2

# entities png
player_png = 'pngs/turret_transparent.png'
bullet_png = 'pngs/bullet.png'
bomb_png = 'pngs/missile_orange.png'
rocket_png = 'pngs/missile_red.png'

# player
player = Player(x=(SCREEN_SIZE[0] / 2), y=SCREEN_SIZE[1] - 120, png=player_png, w=60, h=140)
kills = 0
health = 3
spread = 12  # bullets fire spread

# lists of entities to render
projectiles = []
enemies = []

# render text
def draw_text(text, text_col, x, y):
    img = text_font.render(text, True, text_col)
    screen.blit(img, (x, y))


# spawn bonus
def spawn_bonus():
    pass

# spawn enemy
def spawn_enemy():
    enemy1 = Enemy(rndm(0, SCREEN_SIZE[0]), 0, w=22, h=20, color=GREEN, hp=100 * enemy_hp_mult)
    if random() < 0.1:
        enemy2 = Enemy(rndm(0, SCREEN_SIZE[0]), 0, w=50, h=45, color=GREY, vel=0.2, hp=3000 * enemy_hp_mult)
    else:
        enemy2 = Enemy(rndm(0, SCREEN_SIZE[0]), 0, w=15, h=28, color=YELLOW, vel=1.2, hp=60 * enemy_hp_mult)
    enemy3 = Enemy(rndm(0, SCREEN_SIZE[0]), 0, w=40, h=35, color=BLUE, vel=0.4, hp=600 * enemy_hp_mult)
    enemy4 = Enemy(rndm(0, SCREEN_SIZE[0]), 0, w=30, h=30, color=RED, vel=0.6, hp=150 * enemy_hp_mult)
    enemies.append(choice((enemy1, enemy2, enemy3, enemy4)))


run = True
while run and health:
    level = 0.1 * (kills + 1) / 10
    gun_fire = False
    bomb_fire = False
    rocket_fire = False
    # magic_color = (rndm(0, 255), rndm(0, 255), rndm(0, 255))
    clock.tick(30)
    screen.fill(BG)

    # input handling
    mouse = pygame.mouse.get_pos()
    m_key = pygame.mouse.get_pressed()
    key = pygame.key.get_pressed()

    # handle mouse keys
    if m_key[0]:
        gun_fire = True
    if m_key[2]:
        bomb_fire = True
    if m_key[1]:
        rocket_fire = True

    # handle events
    for event in pygame.event.get():
        # close button - quit game
        if event.type == pygame.QUIT:
            run = False

    # spawn new enemies
    if random() < level:
        spawn_enemy()

    # render player at mouse x coord
    player.x = mouse[0] - 30
    player.upd(screen)

    # check & render enemies
    for enemy in enemies:
        enemy.upd(screen)
        for proj in projectiles:

            # projectile collides with enemy
            if proj.rect and enemy.rect.colliderect(proj.rect):
                if proj.spec in ('nuke'):
                    x, y = proj.x, proj.y,
                    shraps = [Shrapnel(x, y, direct=rndm(0, 360), dmg=100, vel=choice((1, 10)) * 100, duration=3,
                                       spec='nuke') for _ in range(2)]
                    projectiles.extend(shraps)
                if proj.spec in ('rocket'):
                    x, y = proj.x, proj.y,
                    shraps = [Shrapnel(x, y, direct=rndm(0, 360), dmg=200, vel=choice((1, 10)) * 100, duration=10,
                                       spec='nuke') for _ in range(8)]
                    projectiles.extend(shraps)
                if proj.spec in ('bomb',):
                    x, y = proj.x, proj.y,
                    shraps = [Shrapnel(x, y, direct=rndm(0, 360), dmg=300, vel=choice((1, 10)) * 100, duration=15)
                              for _ in range(50)]
                    projectiles.extend(shraps)

                proj.hit(target=enemy)
                if not proj.pierce:
                    projectiles.remove(proj)

        # enemy killed
        if enemy.hp <= 0:
            kills += 1
            enemies.remove(enemy)
        # enemy touch base - minus 1 player hp
        if enemy.y >= SCREEN_SIZE[1]:
            health -= 1
            enemies.remove(enemy)

    # new projectile coordinates
    x, y = player.x + 20, player.y + 30
    x = rndm(x - spread, x + spread)

    # bullets
    if gun_fire:
        rounds = [Projectile(x, y, dmg=rndm(40, 50), facing=1, pierce=5, png=bullet_png, vel=rndm(50, 70), scale=0.18)
                  for _ in range(8)]
        projectiles.extend(rounds)

    # bombs - only one bomb can be present at a time
    if bomb_fire and not any(filter(lambda b: b.spec == 'bomb', projectiles)):
        bomb = Projectile(x, y, dmg=180, facing=1, png=bomb_png, vel=45, scale=0.1, rotate=225, spec='bomb')
        projectiles.append(bomb)

    # rockets - only one rocket can be present at a time
    if rocket_fire and not any(filter(lambda b: b.spec == 'rocket', projectiles)):
        rocket = Projectile(x, y, dmg=180, facing=1, png=rocket_png, vel=15, scale=0.05, spec='rocket')
        projectiles.append(rocket)

    # render projectiles
    for proj in projectiles:
        proj.upd(screen)
        if proj.y < 0:
            projectiles.remove(proj)
        try:
            if isinstance(proj, Shrapnel):
                proj.duration -= 1
                if not proj.duration:
                    projectiles.remove(proj)
        except Exception as e:
            print(e)

    # render stats
    draw_text(text=f'Kills = {kills}', x=20, y=20, text_col=WHITE)
    draw_text(text=f'Enemies = {len(enemies)}', x=20, y=40, text_col=WHITE)
    draw_text(text=f'Health = {health}', x=20, y=60, text_col=WHITE)
    draw_text(text=f'Difficulty = {round(level, 2)}', x=20, y=80, text_col=WHITE)
    draw_text(text=f'FPS = {round(clock.get_fps(), 2)}', x=20, y=100, text_col=WHITE)

    pygame.display.flip()

pygame.quit()
exit('\nGame over')
