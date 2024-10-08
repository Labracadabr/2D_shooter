from random import random, randint, choice
import pygame
from objects import Player, Projectile, Enemy, Shrapnel, Boss
import shaders
from objects import SCREEN_SIZE

# for cv controller (requires webcam and gpu):
# 1. install cuda & pytorch; 2. run pip install ultralyticsplus, cv2; 3. uncomment following lines; 4. press C in game
# import ultralyticsplus
# import cv2
# model = ultralyticsplus.YOLO('lewiswatson/yolov8x-tuned-hand-gestures')
# video = cv2.VideoCapture(0)

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
screen = pygame.display.set_mode(SCREEN_SIZE)
text_font = pygame.font.SysFont('Arial', 18)
clock = pygame.time.Clock()
enemy_hp_mult = 4
MAX_BOMBS = 1
spawn_border_init = int(SCREEN_SIZE[0]/3)
spawn_border = 0
speed_mult = 1
robot = False
cv = False
radial = False
hand_x, hand_y = 0, 0

# entities png
player_png = 'pngs/turret_transparent.png'
bullet_png = 'pngs/bullet.png'
bomb_png = 'pngs/missile_orange.png'
rocket_png = 'pngs/missile_red.png'
fire_png = 'pngs/gunfire.png'
explosion_png = 'pngs/explosions-transparent.png'

# player
player = Player(x=(SCREEN_SIZE[0] / 2), y=SCREEN_SIZE[1] - 120, png=player_png, w=60, h=140, angle=0, radial=False)
kills = 0
health = 3
spread = 8  # bullets fire spread

# lists of entities to render
projectiles = []
enemies = []
debris = []

# render text
def draw_text(text, text_col, x, y):
    img = text_font.render(text, True, text_col)
    screen.blit(img, (x, y))


def load_sprites(sprite_path, grid: tuple, size: tuple, rotate=0) -> list[pygame.surface.Surface]:
    """
    :param sprite_path: file path
    :type grid: grid of sprite images, example grid=(8, 6)
    :param size: size to transform sprite to
    :param rotate: direction to rotate in degrees
    """
    # Load the sprite sheet
    sprite_sheet = pygame.image.load(sprite_path)
    sprite_surfaces = []

    # Get the dimensions of each sprite
    sprite_w = sprite_sheet.get_width() // grid[0]
    sprite_h = sprite_sheet.get_height() // grid[1]

    # Loop through each row and column
    for col in range(grid[0]):
        for row in range(grid[1]):
            # Calculate the x and y position of the current sprite
            x = col * sprite_w
            y = row * sprite_h

            # Create a rectangle for the current sprite
            surface = sprite_sheet.subsurface(pygame.Rect(x, y, sprite_w, sprite_h))
            if rotate:
                surface = pygame.transform.rotate(surface, angle=rotate)
            sprite_surfaces.append(pygame.transform.scale(surface, size))

    return sprite_surfaces


# spawn bonus
def spawn_bonus():
    pass

# spawn enemy
def spawn_enemy():
    x = randint(spawn_border, SCREEN_SIZE[0]-spawn_border)
    enemy1 = Enemy(x, 0, w=22, h=20, color=shaders.green(), vel=0.2 * speed_mult, hp=100 * enemy_hp_mult)
    if random() < 0.1:
        enemy2 = Enemy(x, 0, w=50, h=45, color=shaders.grey(), vel=0.2 * speed_mult, hp=3000 * enemy_hp_mult)
    else:
        enemy2 = Enemy(x, 0, w=15, h=28, color=shaders.yellow(), vel=1.2 * speed_mult, hp=60 * enemy_hp_mult)
    enemy3 = Enemy(x, 0, w=40, h=35, color=shaders.blue(), vel=0.4 * speed_mult, hp=600 * enemy_hp_mult)
    enemy4 = Enemy(x, 0, w=30, h=30, color=shaders.red(), vel=0.6 * speed_mult, hp=150 * enemy_hp_mult)
    enemies.append(choice((enemy1, enemy2, enemy3, enemy4)))

def lowest_enemy_coord(enemies_list: list[Enemy]) -> tuple | None:
    enemies_list.sort(key=lambda enm: enm.y)
    lowest = enemies_list[-1]

    # center coords
    x, y = lowest.rect.center[0], lowest.rect.center[1]
    return x, y


def crosshair(coords: tuple[float, float]):
    x, y = coords
    size = 8

    # line 1
    pygame.draw.line(screen, BLACK, (x+size, y+size), (x-size, y-size), width=4)
    # line 2
    pygame.draw.line(screen, BLACK, (x-size, y+size), (x+size, y-size), width=4)

def rel_centre(x1, y1, x2, y2) -> tuple:
    # Calculate the center of the bounding box
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    # Calculate the relative coordinates
    rel_center_x = center_x / frame.shape[1]
    rel_center_y = center_y / frame.shape[0]
    return round(rel_center_x, 4), round(rel_center_y, 4)


fire_sprites = load_sprites(fire_png, grid=(3, 3), size=(60, 100), rotate=270)
explosion_sprites = load_sprites(explosion_png, (8, 6), size=(60, 80))

run = True
print(f'{run, health = }')
cv_frame = False
while run and health:
    clock.tick(30)
    screen.fill(BG)

    # increasing difficulty
    level = 0.1 * (kills + 1) / 10
    speed_mult = 1 + level / 10
    spawn_border = max(10, int(spawn_border_init / speed_mult))

    # switches
    gun_fire = False
    bomb_fire = False
    rocket_fire = False
    # magic_color = (rndm(0, 255), rndm(0, 255), rndm(0, 255))

    # input handling
    mouse = pygame.mouse.get_pos()
    m_key = pygame.mouse.get_pressed()
    key = pygame.key.get_pressed()

    # handle mouse keys
    if robot or cv:
        gun_fire = bomb_fire = True
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                robot = not robot
            if event.key == pygame.K_c:
                cv = not cv
            if event.key == pygame.K_r:
                radial = not radial

    # spawn new enemies probability
    if random() < level + 0.5:
        spawn_enemy()

    # check & render enemies
    for enemy in enemies[::-1]:
        enemy.upd(screen)
        for proj in projectiles:

            # projectile collides with enemy
            if proj.rect and enemy.rect.colliderect(proj.rect):
                x, y = proj.x, proj.y,
                if proj.spec in ('nuke'):
                    sh = [Shrapnel(x, y, direct=randint(0, 360), dmg=100, vel=choice((1, 10)) * 100, duration=3,
                                   spec='nuke', rgb=shaders.orange()) for _ in range(2)]
                    projectiles.extend(sh)
                if proj.spec in ('rocket'):
                    sh = [Shrapnel(x, y, direct=randint(0, 360), dmg=200, vel=choice((1, 10)) * 100, duration=10,
                                   spec='nuke', rgb=shaders.dark_green()) for _ in range(8)]
                    projectiles.extend(sh)
                if proj.spec in ('bomb',):
                    sh = [Shrapnel(x, y, direct=randint(0, 360), dmg=300, vel=choice((1, 10)) * 100, duration=15)
                          for _ in range(500)]
                    projectiles.extend(sh)

                proj.hit(target=enemy)
                if not proj.pierce:
                    projectiles.remove(proj)

        # enemy killed
        if enemy.hp <= 0:
            kills += 1
            enemies.remove(enemy)
            # debris
            debris.extend(enemy.create_debris())
        # enemy touch base - minus 1 player hp
        if enemy.y >= SCREEN_SIZE[1]:
            health -= 1
            enemies.remove(enemy)

    # render debris
    for deb in debris:
        deb.upd(screen)
        deb.duration -= 1
        if deb.duration < 1:
            debris.remove(deb)

    # move player to the lowest enemy x coord
    if robot and enemies:
        x, y = lowest_enemy_coord(enemies)
        # mark the lowest enemy
        crosshair((x, y))
        player.x = x - 30

    # CV controller
    elif cv:
        cv_frame = not cv_frame
        if cv_frame:
            # read webcam
            _, frame = video.read()
            # perform inference
            results = model.predict(frame)
            # put bbox
            for result in results:
                for box in result.boxes:
                    bbox = box.xyxy.tolist()[0]
                    hand_x, hand_y = rel_centre(*bbox)
                    # conf = box.conf.item()
                    player.x = int((SCREEN_SIZE[0] - SCREEN_SIZE[0] * hand_x) - 30)
                    break
                break

    # move to mouse x coord
    else:
        if radial:
            pass
            angle = player.target_angle(mouse)
        else:
            player.x = mouse[0] - 30
            angle = 90
        hand_x, hand_y = 0, 0
    player.upd(screen)

    # new projectile coordinates
    # x, y = player.x, player.y
    x, y = player.x + 20, player.y + 30
    # x = rndm(x - spread, x + spread)

    # bullets
    if gun_fire:
        rounds = [Projectile(randint(x - spread, x + spread), y, dmg=randint(40, 50), pierce=5,
                  png=bullet_png, vel=randint(50, 70), scale=0.18, angle=angle, rotate=-angle+90) for _ in range(8)]
        projectiles.extend(rounds)
        # gun fire animation
        screen.blit(choice(fire_sprites), (x-28, y-120))

    # bombs - only MAX_BOMBS bombs can be present at a time
    if bomb_fire and len(tuple(filter(lambda b: b.spec == 'bomb', projectiles))) < MAX_BOMBS:
        bomb = Projectile(x, y, dmg=180, png=bomb_png, vel=45, scale=0.1, rotate=225-angle+90, spec='bomb', angle=angle)
        projectiles.append(bomb)

    # rockets - only one rocket can be present at a time
    if rocket_fire and not any(filter(lambda b: b.spec == 'rocket', projectiles)):
        rocket = Projectile(x, y, dmg=180, png=rocket_png, vel=15, scale=0.05, spec='rocket', rotate=angle, angle=angle)
        projectiles.append(rocket)

    # render projectiles
    for proj in projectiles:
        # moved out of screen
        if proj.out_of_screen():
            projectiles.remove(proj)
            continue

        # shrapnel - out of lifetime
        if hasattr(proj, 'duration'):
            proj.duration -= 1
            if not proj.duration:
                projectiles.remove(proj)
                continue
        proj.upd(screen)

    # render stats
    draw_text(text=f'Kills = {kills}', x=20, y=20, text_col=WHITE)
    draw_text(text=f'Enemies = {len(enemies)}', x=20, y=40, text_col=WHITE)
    draw_text(text=f'Health = {health}', x=20, y=60, text_col=WHITE)
    draw_text(text=f'Difficulty = {round(level, 2)}', x=20, y=80, text_col=WHITE)
    draw_text(text=f'FPS = {round(clock.get_fps(), 2)}', x=20, y=100, text_col=WHITE)
    draw_text(text=f'Projectiles = {len(projectiles)}', x=20, y=120, text_col=WHITE)
    draw_text(text=f'Speed = {round(speed_mult, 2)}', x=20, y=140, text_col=WHITE)
    draw_text(text=f'Spawn border = {round(spawn_border, 1)}', x=20, y=160, text_col=WHITE)
    draw_text(text=f'{robot = }', x=20, y=180, text_col=WHITE)
    draw_text(text=f'CV = {cv}', x=20, y=200, text_col=WHITE)
    draw_text(text=f'{hand_x, hand_y = }', x=20, y=220, text_col=WHITE)
    draw_text(text=f'degrees = {player.target_angle(mouse)}', x=20, y=240, text_col=WHITE)

    # show tips
    if kills < 100:
        tips = 'left mouse for gun, right mouse for bombs, mid mouse for nuke, space for aim-bot'
        draw_text(text=tips, x=20, y=SCREEN_SIZE[1]-40, text_col=GREY)

    pygame.display.flip()

pygame.quit()
print(f'\n{kills = }')
exit('Game over')
