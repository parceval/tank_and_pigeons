import pygame
import sys
import random
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank and Pigeons")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Add the background images to a list
background_images = [
    pygame.image.load("images/background1.png"),
    pygame.image.load("images/background2.jpg"),
    pygame.image.load("images/background3.jpg")
]
for i, bg in enumerate(background_images):
    background_images[i] = pygame.transform.scale(bg, (WIDTH, HEIGHT))

background_image_end = pygame.image.load("images/background_end.png")
background_image_end = pygame.transform.scale(background_image_end, (WIDTH, HEIGHT))

current_background = 0
background = background_images[current_background]
prev_background = background
bg_position = 0

tank_clean = pygame.image.load("images/tank_clean.png")
tank_clean = pygame.transform.scale(tank_clean, (100, 100))

tank_hit = pygame.image.load("images/tank_hit.png")
tank_hit = pygame.transform.scale(tank_hit, (100, 100))

tank_explosion = pygame.image.load("images/tank_explosion.png")
tank_explosion = pygame.transform.scale(tank_explosion, (120, 120))

pigeon = pygame.image.load("images/pigeon.png")
pigeon = pygame.transform.scale(pigeon, (50, 50))

bullet = pygame.image.load("images/bullet.png")
bullet = pygame.transform.scale(bullet, (20, 20))

poop = pygame.image.load("images/poop.png")
poop = pygame.transform.scale(poop, (10, 10))

red_particle = pygame.image.load("images/red_particle.png")
red_particle = pygame.transform.scale(red_particle, (12, 12))

shoot_sound = pygame.mixer.Sound("sounds/shoot_sound.wav")
scream_sound = pygame.mixer.Sound("sounds/scream_sound.wav")
tank_hit_sound = pygame.mixer.Sound("sounds/tank_hit.wav")
tank_explosion_sound = pygame.mixer.Sound("sounds/tank_explosion.wav")
pigeon_respawn_sound = pygame.mixer.Sound("sounds/pigeon_respawn.wav")
wave_cleared_sound = pygame.mixer.Sound("sounds/wave_cleared.wav")

font = pygame.font.Font(None, 36)

LEADERBOARD_FILE = "leaderboard.txt"

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return [[0,""]] * 10

    with open(LEADERBOARD_FILE, "r") as f:
        scores = []
        for line in f.readlines():
            x = line.strip().split(":")
            scores.append([int(x[1]), x[0]])
    return scores

def update_leaderboard(score, name):
    scores = load_leaderboard()
    scores.append((score, name))
    scores.sort(key=lambda x: x[0], reverse=True)
    scores = scores[:10]

    with open(LEADERBOARD_FILE, "w") as f:
        for score, name in scores:
            f.write(f"{name}:{score}\n")
    return scores

def display_leaderboard(win):
    scores = load_leaderboard()
    for i, (score, name) in enumerate(scores):
        draw_text(f"{i + 1}. {name}: {score}", WIDTH // 2 - 100, 50 + i * 30, "WHITE")

def prompt_name():
    name = ""
    prompt_text = "Enter your name: "
    while True:
        win.blit(background, (0, 0))
        display_leaderboard(win)
        draw_text(prompt_text + name,  WIDTH // 2 - 200, HEIGHT // 2 + 90, "WHITE")

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 10:
                    name += event.unicode

class GameObject:
    def __init__(self, x, y, image, speed=0):
        self.x = x
        self.y = y
        self.image = image
        self.speed = speed

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

def respawn_pigeon():
    return GameObject(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT // 2), pigeon, random.choice([-3, -2, -1, 1, 2, 3]))

def draw_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    win.blit(text_surface, (x, y))

def pigeon_explosion(x, y, num_particles):
    particles = [GameObject(x, y, red_particle) for _ in range(num_particles)]
    for p in particles:
        p.speed_x = random.uniform(-2, 2)
        p.speed_y = random.uniform(-2, 2)
        p.age = 0
        p.landed=False
    return particles

def change_background():
    global current_background, background, prev_background, bg_position
    current_background = (current_background + 1) % len(background_images)
    prev_background = background
    background = background_images[current_background]
    bg_position = WIDTH

def end_background():
    global background
    background = background_image_end

def main():
    global background, bg_position, prev_background
    # change_background()
    tank_obj = GameObject(WIDTH // 2 - 50, HEIGHT - 120, tank_clean)
    pigeons = [respawn_pigeon() for _ in range(10)]
    background = background_images[current_background]
    bullets = []
    poops = []
    particles = []
    score = 0
    lives = 5
    game_over = False
    hit_time = None
    end_idle_time = None
    tank_img = tank_clean

    clock = pygame.time.Clock()
    running = True

    while running:
        end_idle = True if end_idle_time is not None and pygame.time.get_ticks() - end_idle_time > 1000 else False
        clock.tick(60)
        if bg_position <= 0:
            win.blit(background, (0, 0))
        else:
            win.blit(prev_background, (bg_position-WIDTH, 0))
            win.blit(background, (bg_position, 0))
            bg_position-=40

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bullets.append(GameObject(tank_obj.x + 40, tank_obj.y, bullet))
                    pygame.mixer.Channel(2).play(shoot_sound)
                elif event.key == pygame.K_SPACE and game_over:
                    player_name = prompt_name()
                    update_leaderboard(score, player_name)
                    main()  # Restart the game

        if hit_time is not None and pygame.time.get_ticks() - hit_time < 1000:
            tank_img = tank_hit
        else:
            tank_img = tank_clean

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and tank_obj.x > 0 and not game_over:
            tank_obj.x -= 5
            tank_obj.image = pygame.transform.flip(tank_img, True, False)
        if keys[pygame.K_RIGHT] and tank_obj.x < WIDTH - 100 and not game_over:
            tank_obj.x += 5
            tank_obj.image = pygame.transform.flip(tank_img, False, False)

        if lives <= 0:
            if not game_over:
                pygame.mixer.Channel(3).play(tank_explosion_sound)
                end_idle_time = pygame.time.get_ticks()
                tank_obj.image = tank_explosion
            game_over = True
            if end_idle:
                end_background()
                draw_text("GAME OVER", WIDTH // 2 - 100, HEIGHT // 2 + 90, "RED")
                display_leaderboard(win)
                draw_text("Press SPACE to restart", WIDTH // 2 - 150, HEIGHT // 2 + 140, "WHITE")

        for b in bullets:
            b.y -= 10
            if b.y < -20:
                bullets.remove(b)

            for p in pigeons:
                if b.x < p.x + 50 and b.x > p.x - 20 and b.y < p.y + 50 and b.y > p.y - 20:
                    bullets.remove(b)
                    pigeons.remove(p)
                    pygame.mixer.Channel(4).play(scream_sound)
                    score += 1
                    particles.extend(pigeon_explosion(p.x, p.y, int(random.uniform(10, 100))))
                    pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # Schedule respawn event in 1 second
                    break

        for p in pigeons:
            p.x += p.speed
            if p.x < 0 or p.x > WIDTH - 50:
                p.speed = -p.speed
                p.image = pygame.transform.flip(p.image, True, False)

            if not game_over and random.random() < 0.01:  # 1% chance to poop
                poops.append(GameObject(p.x + 20, p.y + 50, poop))

        for poop_obj in poops:
            poop_obj.y += 5
            if poop_obj.y > HEIGHT:
                poops.remove(poop_obj)

            if tank_obj.x < poop_obj.x + 10 and tank_obj.x + 100 > poop_obj.x and tank_obj.y < poop_obj.y + 10 and tank_obj.y + 100 > poop_obj.y:
                poops.remove(poop_obj)
                lives -= 1
                hit_time = pygame.time.get_ticks()
                pygame.mixer.Channel(6).play(tank_hit_sound)
                break

        for particle in particles:
            if particle.landed == False:
                particle.x += particle.speed_x
                particle.y += particle.speed_y + (0.1 * particle.age)
            particle.age+=1

            if particle.y > HEIGHT - int(random.uniform(10, 50)):
                particle.landed=True;
                # particles.remove(particle)

        if not end_idle or not game_over: tank_obj.draw(win)
        if not game_over:
            for p in pigeons:
                p.draw(win)
            for b in bullets:
                b.draw(win)
            for poop_obj in poops:
                poop_obj.draw(win)
            for particle in particles:
                particle.draw(win)

        if not game_over:
            draw_text(f"Score: {score}", 10, 10, "PURPLE")
            draw_text(f"Lives: {lives if lives > 0 else '0'}", 10, 40, "PURPLE")

        if len(pigeons) == 0:
            score += 10
            pygame.mixer.Channel(5).play(wave_cleared_sound)
            pigeons = [respawn_pigeon() for _ in range(10)]
            change_background()
            particles=[]

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
