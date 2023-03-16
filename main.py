#!/bin/env python3

import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank and Pigeons")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game objects
tank = pygame.image.load("tank.png")
tank = pygame.transform.scale(tank, (100, 100))

pigeon = pygame.image.load("pigeon.png")
pigeon = pygame.transform.scale(pigeon, (50, 50))

bullet = pygame.image.load("bullet.png")
bullet = pygame.transform.scale(bullet, (20, 20))

class GameObject:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

def main():
    tank_obj = GameObject(WIDTH // 2 - 50, HEIGHT - 120, tank)
    pigeons = [GameObject(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT // 2), pigeon) for _ in range(10)]
    bullets = []

    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(60)
        win.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(GameObject(tank_obj.x + 40, tank_obj.y, bullet))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and tank_obj.x > 0:
            tank_obj.x -= 5
        if keys[pygame.K_RIGHT] and tank_obj.x < WIDTH - 100:
            tank_obj.x += 5

        for b in bullets:
            b.y -= 10
            if b.y < -20:
                bullets.remove(b)

            for p in pigeons:
                if b.x < p.x + 50 and b.x > p.x - 20 and b.y < p.y + 50 and b.y > p.y - 20:
                    bullets.remove(b)
                    pigeons.remove(p)
                    break

        tank_obj.draw(win)
        for p in pigeons:
            p.draw(win)
        for b in bullets:
            b.draw(win)

        pygame.display.update()

if __name__ == "__main__":
    main()
