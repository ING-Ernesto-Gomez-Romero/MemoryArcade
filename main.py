from __future__ import annotations

import random
import sys
import time
from dataclasses import dataclass

import pygame


WIDTH, HEIGHT = 960, 680
FPS = 60
BACKGROUND = (17, 24, 39)
PANEL = (31, 41, 55)
WHITE = (245, 247, 250)
MUTED = (156, 163, 175)
BLUE = (59, 130, 246)
CYAN = (45, 212, 191)
YELLOW = (250, 204, 21)
RED = (248, 113, 113)
CARD_COLORS = [
    (244, 114, 182),
    (96, 165, 250),
    (52, 211, 153),
    (251, 191, 36),
    (167, 139, 250),
    (251, 146, 60),
    (34, 211, 238),
    (248, 113, 113),
]


def draw_text(surface, text, size, color, center=None, topleft=None, bold=False):
    font = pygame.font.SysFont("segoeui", size, bold=bold)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = center
    if topleft:
        rect.topleft = topleft
    surface.blit(rendered, rect)
    return rect


class Button:
    def __init__(self, rect, label, accent=BLUE):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.accent = accent

    def draw(self, surface, mouse):
        hovered = self.rect.collidepoint(mouse)
        color = self.accent if hovered else PANEL
        pygame.draw.rect(surface, color, self.rect, border_radius=7)
        pygame.draw.rect(surface, self.accent, self.rect, width=2, border_radius=7)
        draw_text(surface, self.label, 24, WHITE, center=self.rect.center, bold=True)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


@dataclass
class MemoryCard:
    value: int
    rect: pygame.Rect
    revealed: bool = False
    matched: bool = False

    def draw(self, surface):
        if self.revealed or self.matched:
            pygame.draw.rect(surface, CARD_COLORS[self.value], self.rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=8)
            draw_text(surface, chr(65 + self.value), 42, BACKGROUND, center=self.rect.center, bold=True)
        else:
            pygame.draw.rect(surface, PANEL, self.rect, border_radius=8)
            pygame.draw.rect(surface, BLUE, self.rect, width=2, border_radius=8)
            draw_text(surface, "?", 38, MUTED, center=self.rect.center, bold=True)


class MemoryGame:
    def __init__(self):
        self.reset()

    def reset(self):
        values = list(range(8)) * 2
        random.shuffle(values)
        card_w, card_h, gap = 130, 105, 14
        start_x = (WIDTH - (card_w * 4 + gap * 3)) // 2
        start_y = 145
        self.cards = []
        for index, value in enumerate(values):
            row, column = divmod(index, 4)
            rect = pygame.Rect(start_x + column * (card_w + gap), start_y + row * (card_h + gap), card_w, card_h)
            self.cards.append(MemoryCard(value, rect))
        self.selected = []
        self.hide_at = 0.0
        self.moves = 0
        self.started_at = time.monotonic()
        self.finished_at = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.reset()
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1 or len(self.selected) == 2:
            return
        for card in self.cards:
            if card.rect.collidepoint(event.pos) and not card.revealed and not card.matched:
                card.revealed = True
                self.selected.append(card)
                if len(self.selected) == 2:
                    self.moves += 1
                    if self.selected[0].value == self.selected[1].value:
                        for selected in self.selected:
                            selected.matched = True
                        self.selected.clear()
                        if all(item.matched for item in self.cards):
                            self.finished_at = time.monotonic()
                    else:
                        self.hide_at = time.monotonic() + 0.75
                break

    def update(self):
        if len(self.selected) == 2 and time.monotonic() >= self.hide_at:
            for card in self.selected:
                card.revealed = False
            self.selected.clear()

    def draw(self, surface):
        elapsed = int((self.finished_at or time.monotonic()) - self.started_at)
        draw_text(surface, "MEMORAMA", 38, WHITE, center=(WIDTH // 2, 50), bold=True)
        draw_text(surface, f"Movimientos: {self.moves}", 22, MUTED, topleft=(190, 93))
        draw_text(surface, f"Tiempo: {elapsed}s", 22, MUTED, topleft=(650, 93))
        for card in self.cards:
            card.draw(surface)
        if self.finished_at:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 10, 20, 205))
            surface.blit(overlay, (0, 0))
            draw_text(surface, "Partida completada", 46, CYAN, center=(WIDTH // 2, 285), bold=True)
            draw_text(surface, f"{self.moves} movimientos en {elapsed} segundos", 25, WHITE, center=(WIDTH // 2, 345))
            draw_text(surface, "Presiona R para volver a jugar", 21, MUTED, center=(WIDTH // 2, 400))


class SnakeGame:
    CELL = 24
    COLS = 30
    ROWS = 22
    BOARD_W = CELL * COLS
    BOARD_H = CELL * ROWS
    BOARD_X = (WIDTH - BOARD_W) // 2
    BOARD_Y = 110

    def __init__(self):
        self.reset()

    def reset(self):
        self.snake = [(15, 11), (14, 11), (13, 11)]
        self.direction = (1, 0)
        self.next_direction = self.direction
        self.food = self.new_food()
        self.score = 0
        self.dead = False
        self.paused = False
        self.last_move = time.monotonic()

    def new_food(self):
        available = [(x, y) for x in range(self.COLS) for y in range(self.ROWS) if (x, y) not in self.snake]
        return random.choice(available)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_r and self.dead:
            self.reset()
            return
        if event.key == pygame.K_p and not self.dead:
            self.paused = not self.paused
            return
        choices = {
            pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
            pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
            pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
            pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
        }
        candidate = choices.get(event.key)
        if candidate and candidate != (-self.direction[0], -self.direction[1]):
            self.next_direction = candidate

    def update(self):
        interval = max(0.07, 0.16 - self.score * 0.004)
        if self.dead or self.paused or time.monotonic() - self.last_move < interval:
            return
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        head = (head_x + dx, head_y + dy)
        self.last_move = time.monotonic()
        if head[0] < 0 or head[0] >= self.COLS or head[1] < 0 or head[1] >= self.ROWS or head in self.snake[:-1]:
            self.dead = True
            return
        self.snake.insert(0, head)
        if head == self.food:
            self.score += 1
            self.food = self.new_food()
        else:
            self.snake.pop()

    def draw(self, surface):
        draw_text(surface, "SNAKE", 38, WHITE, center=(WIDTH // 2, 42), bold=True)
        draw_text(surface, f"Puntuacion: {self.score}", 22, MUTED, center=(WIDTH // 2, 82))
        board = pygame.Rect(self.BOARD_X, self.BOARD_Y, self.BOARD_W, self.BOARD_H)
        pygame.draw.rect(surface, PANEL, board, border_radius=7)
        for x, y in self.snake:
            rect = pygame.Rect(self.BOARD_X + x * self.CELL + 2, self.BOARD_Y + y * self.CELL + 2, self.CELL - 4, self.CELL - 4)
            pygame.draw.rect(surface, CYAN if (x, y) == self.snake[0] else BLUE, rect, border_radius=5)
        food_rect = pygame.Rect(self.BOARD_X + self.food[0] * self.CELL + 4, self.BOARD_Y + self.food[1] * self.CELL + 4, self.CELL - 8, self.CELL - 8)
        pygame.draw.circle(surface, RED, food_rect.center, food_rect.width // 2)
        if self.dead or self.paused:
            overlay = pygame.Surface((self.BOARD_W, self.BOARD_H), pygame.SRCALPHA)
            overlay.fill((5, 10, 20, 190))
            surface.blit(overlay, board.topleft)
            title = "Pausa" if self.paused else "Fin de la partida"
            hint = "P para continuar" if self.paused else "R para reiniciar"
            draw_text(surface, title, 46, YELLOW if self.paused else RED, center=board.center, bold=True)
            draw_text(surface, hint, 22, WHITE, center=(board.centerx, board.centery + 55))


class Arcade:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Memory Arcade")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.state = "menu"
        self.memory = MemoryGame()
        self.snake = SnakeGame()
        self.memory_button = Button((WIDTH // 2 - 190, 290, 380, 65), "Jugar Memorama", BLUE)
        self.snake_button = Button((WIDTH // 2 - 190, 375, 380, 65), "Jugar Snake", CYAN)
        self.exit_button = Button((WIDTH // 2 - 190, 460, 380, 58), "Salir", RED)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                if self.state == "menu":
                    if self.memory_button.clicked(event):
                        self.memory.reset()
                        self.state = "memory"
                    elif self.snake_button.clicked(event):
                        self.snake.reset()
                        self.state = "snake"
                    elif self.exit_button.clicked(event):
                        pygame.quit()
                        sys.exit()
                elif self.state == "memory":
                    self.memory.handle_event(event)
                elif self.state == "snake":
                    self.snake.handle_event(event)

            if self.state == "memory":
                self.memory.update()
            elif self.state == "snake":
                self.snake.update()
            self.draw()
            self.clock.tick(FPS)

    def draw(self):
        self.screen.fill(BACKGROUND)
        if self.state == "menu":
            draw_text(self.screen, "MEMORY ARCADE", 54, WHITE, center=(WIDTH // 2, 150), bold=True)
            draw_text(self.screen, "Dos juegos clasicos creados con Python y Pygame", 23, MUTED, center=(WIDTH // 2, 210))
            mouse = pygame.mouse.get_pos()
            self.memory_button.draw(self.screen, mouse)
            self.snake_button.draw(self.screen, mouse)
            self.exit_button.draw(self.screen, mouse)
            draw_text(self.screen, "Selecciona un juego", 18, MUTED, center=(WIDTH // 2, 570))
        elif self.state == "memory":
            self.memory.draw(self.screen)
            draw_text(self.screen, "Esc: menu | R: reiniciar", 17, MUTED, center=(WIDTH // 2, 650))
        else:
            self.snake.draw(self.screen)
            draw_text(self.screen, "Flechas/WASD: mover | P: pausa | Esc: menu", 17, MUTED, center=(WIDTH // 2, 660))
        pygame.display.flip()


if __name__ == "__main__":
    Arcade().run()
