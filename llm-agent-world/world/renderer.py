import pygame

TILE      = 60
MARGIN    = 4
INFO_H    = 120
FPS       = 10

COLORS = {
    "#": (40,  40,  40),
    ".": (200, 200, 180),
    "?": (100, 100, 100),
    "K": (255, 210,  50),
    "D": (160,  80,  20),
    "G": (50,  200,  80),
    "A": (80,  140, 255),
}

TEXT_COLOR   = (230, 230, 230)
BG_COLOR     = (20,  20,  20)
INFO_BG      = (30,  30,  30)
SUCCESS_COL  = (50,  200,  80)
FAIL_COL     = (220,  60,  60)


class Renderer:
    def __init__(self, rows: int, cols: int):
        pygame.init()
        pygame.display.set_caption("LLM Agent World")
        self.rows  = rows
        self.cols  = cols
        self.w     = cols * TILE
        self.h     = rows * TILE + INFO_H
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.clock  = pygame.time.Clock()
        self.font   = pygame.font.SysFont("monospace", 15)
        self.big    = pygame.font.SysFont("monospace", 20, bold=True)

    def draw(self, grid, agent, step: int, last_action: str, last_outcome: str, last_events: list):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        self.screen.fill(BG_COLOR)
        self._draw_grid(grid, agent)
        self._draw_info(step, last_action, last_outcome, last_events, agent)
        pygame.display.flip()
        self.clock.tick(FPS)

    def _draw_grid(self, grid, agent):
        for y, row in enumerate(grid.cells):
            for x, ch in enumerate(row):
                color = COLORS.get(ch, (150, 150, 150))
                rect  = pygame.Rect(x * TILE + MARGIN, y * TILE + MARGIN,
                                    TILE - MARGIN * 2, TILE - MARGIN * 2)
                pygame.draw.rect(self.screen, color, rect, border_radius=6)

                if ch not in ("#", "."):
                    label = self.font.render(ch, True, (20, 20, 20))
                    self.screen.blit(label, label.get_rect(center=rect.center))

        # draw agent on top
        ax, ay = agent.pos
        rect = pygame.Rect(ax * TILE + MARGIN, ay * TILE + MARGIN,
                           TILE - MARGIN * 2, TILE - MARGIN * 2)
        pygame.draw.rect(self.screen, COLORS["A"], rect, border_radius=6)
        label = self.font.render("A", True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=rect.center))

        if agent.has_key:
            dot_rect = pygame.Rect(ax * TILE + TILE - 18, ay * TILE + 6, 10, 10)
            pygame.draw.ellipse(self.screen, COLORS["K"], dot_rect)

    def _draw_info(self, step, action, outcome, events, agent):
        y0 = self.rows * TILE
        pygame.draw.rect(self.screen, INFO_BG, (0, y0, self.w, INFO_H))
        pygame.draw.line(self.screen, (60, 60, 60), (0, y0), (self.w, y0), 2)

        outcome_col = SUCCESS_COL if outcome == "success" else FAIL_COL
        step_surf   = self.big.render(f"Step {step:02d}", True, TEXT_COLOR)
        action_surf = self.big.render(f"{action}", True, TEXT_COLOR)
        outcome_surf= self.big.render(outcome.upper(), True, outcome_col)

        self.screen.blit(step_surf,    (16, y0 + 12))
        self.screen.blit(action_surf,  (16, y0 + 38))
        self.screen.blit(outcome_surf, (16, y0 + 64))

        inv = "Key: YES" if agent.has_key else "Key: no"
        inv_surf = self.font.render(inv, True, COLORS["K"] if agent.has_key else TEXT_COLOR)
        self.screen.blit(inv_surf, (self.w - 120, y0 + 12))

        if events:
            ev_surf = self.font.render(", ".join(events), True, (180, 180, 255))
            self.screen.blit(ev_surf, (16, y0 + 92))

    def pause(self, ms: int):
        pygame.time.wait(ms)

    def close(self):
        pygame.quit()
