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

background = pygame.image.load("background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

tank = pygame.image.load("tank.png")
tank = pygame.transform.scale(tank, (100, 100))

tank_explosion = pygame.image.load("tank_explosion.png")
tank_explosion = pygame.transform.scale(tank_explosion, (120, 120))

pigeon = pygame.image.load("pigeon.png")
pigeon = pygame.transform.scale(pigeon, (50, 50))

bullet = pygame.image.load("bullet.png")
bullet = pygame.transform.scale(bullet, (20, 20))

poop = pygame.image.load("poop.png")
poop = pygame.transform.scale(poop, (10, 10))

red_particle = pygame.image.load("red_particle.png")
red_particle = pygame.transform.scale(red_particle, (12, 12))

shoot_sound = pygame.mixer.Sound("shoot_sound.wav")
scream_sound = pygame.mixer.Sound("scream_sound.wav")
tank_hit_sound = pygame.mixer.Sound("tank_hit.wav")
pigeon_respawn_sound = pygame.mixer.Sound("pigeon_respawn.wav")
wave_cleared_sound = pygame.mixer.Sound("wave_cleared.wav")

font = pygame.font.Font(None, 36)

LEADERBOARD_FILE = "leaderboard.txt"

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return [0] * 10

    with open(LEADERBOARD_FILE, "r") as f:
        scores = [int(line.strip()) for line in f.readlines()]
    return scores

def update_leaderboard(score):
    scores = load_leaderboard()
    scores.append(score)
    scores.sort(reverse=True)
    scores = scores[:10]

    with open(LEADERBOARD_FILE, "w") as f:
        for score in scores:
            f.write(str(score) + "\n")
    return scores

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
    return particles

def main():
    tank_obj = GameObject(WIDTH // 2 - 50, HEIGHT - 120, tank)
    pigeons = [respawn_pigeon() for _ in range(10)]
    bullets = []
    poops = []
    particles = []
    score = 0
    lives = 5
    game_over = False

    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(60)
        win.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bullets.append(GameObject(tank_obj.x + 40, tank_obj.y, bullet))
                    shoot_sound.play()
                elif event.key == pygame.K_SPACE and game_over:
                    updated_scores = update_leaderboard(score)
                    print("Updated Leaderboard:")
                    for i, s in enumerate(updated_scores):
                        print(f"{i + 1}. {s}")
                    main()  # Restart the game

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and tank_obj.x > 0 and not game_over:
            tank_obj.x -= 5
            tank_obj.image = pygame.transform.flip(tank, True, False)
        if keys[pygame.K_RIGHT] and tank_obj.x < WIDTH - 100 and not game_over:
            tank_obj.x += 5
            tank_obj.image = pygame.transform.flip(tank, False, False)

        if lives <= 0:
            game_over = True
            draw_text("GAME OVER", WIDTH // 2 - 100, HEIGHT // 2 - 50)
            draw_text(f"Final Score: {score}", WIDTH // 2 - 100, HEIGHT // 2)
            draw_text("Press SPACE to restart", WIDTH // 2 - 150, HEIGHT // 2 + 50)
            tank_obj.image = tank_explosion

        for b in bullets:
            b.y -= 10
            if b.y < -20:
                bullets.remove(b)

            for p in pigeons:
                if b.x < p.x + 50 and b.x > p.x - 20 and b.y < p.y + 50 and b.y > p.y - 20:
                    bullets.remove(b)
                    pigeons.remove(p)
                    scream_sound.play()
                    score += 100
                    particles.extend(pigeon_explosion(p.x, p.y, 10))
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
                tank_hit_sound.play()
                break

        for particle in particles:
            particle.x += particle.speed_x
            particle.y += particle.speed_y
            if particle.y > HEIGHT:
                particles.remove(particle)

        tank_obj.draw(win)
        for p in pigeons:
            p.draw(win)
        for b in bullets:
            b.draw(win)
        for poop_obj in poops:
            poop_obj.draw(win)
        for particle in particles:
            particle.draw(win)

        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"Lives: {lives}", 10, 40)

        if len(pigeons) == 0:
            score += 1000
            wave_cleared_sound.play()
            pigeons = [respawn_pigeon() for _ in range(10)]

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
