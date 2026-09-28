import pygame
import sys
import time

from ai.astar import a_star
from ai.minimax import get_best_action


# =========================================================
# INITIALIZATION
# =========================================================

pygame.init()

WIDTH = 1200
HEIGHT = 750

SCREEN = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "AI Battle Arena - A* + Minimax"
)

CLOCK = pygame.time.Clock()


# =========================================================
# COLORS
# =========================================================

BG_COLOR = (10, 15, 25)
PANEL_COLOR = (18, 25, 38)
PANEL_LIGHT = (25, 34, 50)

GRID_COLOR = (45, 58, 78)
GRID_ACTIVE = (55, 75, 100)

WHITE = (240, 245, 250)
GRAY = (150, 160, 175)

CYAN = (40, 220, 240)
GREEN = (70, 220, 130)
RED = (245, 80, 90)
YELLOW = (255, 205, 70)
ORANGE = (255, 145, 60)

BLUE = (70, 130, 255)
PURPLE = (170, 100, 240)

BLACK = (5, 8, 15)


# =========================================================
# FONTS
# =========================================================

FONT_SMALL = pygame.font.SysFont(
    "arial",
    14
)

FONT_NORMAL = pygame.font.SysFont(
    "arial",
    17
)

FONT_MEDIUM = pygame.font.SysFont(
    "arial",
    20,
    bold=True
)

FONT_LARGE = pygame.font.SysFont(
    "arial",
    28,
    bold=True
)

FONT_TITLE = pygame.font.SysFont(
    "arial",
    30,
    bold=True
)


# =========================================================
# GRID SETTINGS
# =========================================================

ROWS = 8
COLS = 12

CELL_SIZE = 55

GRID_X = 45
GRID_Y = 130

GRID_WIDTH = COLS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE


# =========================================================
# GAME SETTINGS
# =========================================================

MAX_HP = 100

PLAYER_DAMAGE = 20
AI_DAMAGE = 15

ATTACK_RANGE = 1

AI_DEPTH = 3

AI_THINK_DELAY = 1200

# =========================================================
# LEVEL PROGRESSION
# =========================================================
# Five combat stages. Level 5 is the final boss and ends the run
# when defeated. The AI gets stronger through HP, damage and search
# depth, while the player gets a fresh 100 HP at each new stage.
LEVEL_CONFIG = {
    1: {"name": "ROOKIE FIGHTER", "hp": 100, "damage": 15, "depth": 3, "reward": 100, "survival_threshold": 25},
    2: {"name": "VANGUARD FIGHTER", "hp": 120, "damage": 16, "depth": 3, "reward": 150, "survival_threshold": 30},
    3: {"name": "ELITE FIGHTER", "hp": 145, "damage": 18, "depth": 3, "reward": 200, "survival_threshold": 32},
    4: {"name": "COMMANDER", "hp": 170, "damage": 20, "depth": 4, "reward": 250, "survival_threshold": 35},
    5: {"name": "FINAL BOSS", "hp": 220, "damage": 24, "depth": 4, "reward": 1000, "survival_threshold": 45},
}

FINAL_LEVEL = 5

# Player gets a reasonable response window each turn.
PLAYER_RESPONSE_TIME = 10000

# When the AI becomes critically weak, it tries to disengage
# instead of standing still and waiting to be killed.
AI_LOW_HP_THRESHOLD = 25

# Survival mode is temporary. The wounded AI may retreat only a
# couple of times before it must re-engage. Staying wounded for too
# long also causes a small HP drain.
SURVIVAL_MAX_RETREAT_TURNS = 2
SURVIVAL_HP_DRAIN = 5
SURVIVAL_ATTACK_HEAL = 8

# ---------------------------------------------------------
# HYBRID AI (A* + MINIMAX)
#
# True  -> When the player is out of attack range, A*
#          decides the actual step toward the player
#          (it can go around obstacles).
#          Minimax decides everything once the AI is
#          in attack range (ATTACK / DEFEND / MOVE).
#
# False -> Minimax alone decides every action.
#          (A* is only calculated and displayed.)
# ---------------------------------------------------------

USE_ASTAR_MOVEMENT = True


# =========================================================
# OBSTACLES
# =========================================================

OBSTACLES = {
    (1, 4),
    (1, 5),

    (2, 4),

    (3, 7),
    (3, 8),

    (4, 2),
    (4, 3),

    (5, 7),

    (6, 5),
    (6, 6),
    (6, 8),

    (7, 8),
    (7, 9),

}


# =========================================================
# GAME STATE
#
# Shield (defend) rule used by BOTH main.py and minimax.py:
#   - DEFEND gives a shield.
#   - The shield halves the next hit and is then used up.
#   - The shield is also lost if that unit moves.
# =========================================================

player_position = (2, 2)
ai_position = (5, 9)

player_hp = MAX_HP
ai_max_hp = MAX_HP
ai_hp = ai_max_hp

# Progression
level = 1
score = 0
ai_name = LEVEL_CONFIG[level]["name"]
final_victory = False

player_defending = False
ai_defending = False

turn = "PLAYER"

game_over = False

winner = None

ai_thinking = False

ai_turn_ready_time = 0
player_turn_started_at = 0

ai_action_text = "Waiting..."

# Survival-mode tracking
ai_survival_mode = False
ai_survival_turns = 0

battle_log = []


# =========================================================
# AI METRICS
# =========================================================

astar_path = []

astar_nodes = 0
astar_path_cost = 0
astar_time = 0.0

minimax_nodes = 0
minimax_pruned = 0
minimax_time = 0.0

minimax_score = 0

search_depth = AI_DEPTH


# =========================================================
# ANIMATION STATE
# =========================================================

attack_animation = False
attack_animation_start = 0

attack_from = None
attack_to = None

damage_number = None
damage_number_start = 0
damage_number_position = None

shield_animation = False
shield_animation_start = 0
shield_owner = None

MOVE_ANIMATION_TIME = 180


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def add_log(message):

    battle_log.append(message)

    if len(battle_log) > 8:
        battle_log.pop(0)


def reset_metrics():

    global astar_path
    global astar_nodes
    global astar_path_cost
    global astar_time

    global minimax_nodes
    global minimax_pruned
    global minimax_time
    global minimax_score

    astar_path = []

    astar_nodes = 0
    astar_path_cost = 0
    astar_time = 0.0

    minimax_nodes = 0
    minimax_pruned = 0
    minimax_time = 0.0
    minimax_score = 0


def reset_game():

    global player_position
    global ai_position

    global player_hp
    global ai_max_hp
    global ai_hp

    global level
    global score
    global ai_name
    global final_victory

    global player_defending
    global ai_defending

    global turn
    global game_over
    global winner

    global ai_thinking
    global ai_turn_ready_time
    global player_turn_started_at
    global ai_action_text
    global ai_survival_mode
    global ai_survival_turns

    global battle_log

    global attack_animation
    global damage_number
    global shield_animation
    global shield_owner

    player_position = (2, 2)
    ai_position = (5, 9)

    level = 1
    score = 0
    ai_name = LEVEL_CONFIG[level]["name"]
    final_victory = False

    player_hp = MAX_HP
    ai_max_hp = MAX_HP
    ai_hp = ai_max_hp

    player_defending = False
    ai_defending = False

    turn = "PLAYER"

    game_over = False
    winner = None

    ai_thinking = False
    ai_turn_ready_time = 0
    player_turn_started_at = pygame.time.get_ticks()

    ai_action_text = "Waiting..."

    ai_survival_mode = False
    ai_survival_turns = 0

    battle_log = []

    attack_animation = False
    damage_number = None
    shield_animation = False
    shield_owner = None

    reset_metrics()

    add_log("Battle started — Level 1.")
    add_log("Your turn. You have 10 seconds to respond.")


# =========================================================
# GRID HELPERS
# =========================================================

def cell_rect(position):

    row, col = position

    return pygame.Rect(
        GRID_X + col * CELL_SIZE,
        GRID_Y + row * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )


def cell_center(position):

    rect = cell_rect(position)

    return rect.center


def is_inside_grid(position):

    row, col = position

    return (
        0 <= row < ROWS
        and
        0 <= col < COLS
    )


def get_adjacent_positions(position):

    row, col = position

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ]

    positions = []

    for dr, dc in directions:

        new_position = (
            row + dr,
            col + dc
        )

        if is_inside_grid(new_position):
            positions.append(new_position)

    return positions


# =========================================================
# DISTANCE
# =========================================================

def get_distance(a, b):

    return (
        abs(a[0] - b[0])
        +
        abs(a[1] - b[1])
    )


def can_attack(attacker, target):

    return (
        get_distance(
            attacker,
            target
        )
        <= ATTACK_RANGE
    )


# =========================================================
# DRAW TEXT
# =========================================================

def draw_text(
    text,
    position,
    font=FONT_NORMAL,
    color=WHITE
):

    surface = font.render(
        str(text),
        True,
        color
    )

    SCREEN.blit(
        surface,
        position
    )


# =========================================================
# DRAW CENTERED TEXT
# =========================================================

def draw_center_text(
    text,
    center,
    font=FONT_NORMAL,
    color=WHITE
):

    surface = font.render(
        str(text),
        True,
        color
    )

    rect = surface.get_rect(
        center=center
    )

    SCREEN.blit(
        surface,
        rect
    )


# =========================================================
# DRAW PANEL
# =========================================================

def draw_panel(
    rect,
    title=None
):

    pygame.draw.rect(
        SCREEN,
        PANEL_COLOR,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        SCREEN,
        (40, 52, 70),
        rect,
        width=1,
        border_radius=12
    )

    if title:

        draw_text(
            title,
            (
                rect.x + 16,
                rect.y + 12
            ),
            FONT_MEDIUM,
            WHITE
        )


# =========================================================
# HP BAR
# =========================================================

def draw_hp_bar(
    x,
    y,
    width,
    height,
    hp,
    max_hp,
    label,
    bar_color
):

    draw_text(
        f"{label}: {hp}/{max_hp}",
        (x, y - 24),
        FONT_NORMAL,
        WHITE
    )

    background = pygame.Rect(
        x,
        y,
        width,
        height
    )

    pygame.draw.rect(
        SCREEN,
        (45, 50, 60),
        background,
        border_radius=6
    )

    ratio = max(
        0,
        min(
            hp / max_hp,
            1
        )
    )

    foreground = pygame.Rect(
        x,
        y,
        int(width * ratio),
        height
    )

    pygame.draw.rect(
        SCREEN,
        bar_color,
        foreground,
        border_radius=6
    )

    pygame.draw.rect(
        SCREEN,
        (80, 90, 105),
        background,
        width=1,
        border_radius=6
    )


# =========================================================
# DRAW GRID
# =========================================================

def draw_grid():

    for row in range(ROWS):

        for col in range(COLS):

            position = (
                row,
                col
            )

            rect = cell_rect(
                position
            )

            if position in OBSTACLES:

                pygame.draw.rect(
                    SCREEN,
                    (35, 40, 52),
                    rect,
                    border_radius=5
                )

                pygame.draw.rect(
                    SCREEN,
                    (70, 78, 95),
                    rect,
                    width=2,
                    border_radius=5
                )

                draw_center_text(
                    "■",
                    rect.center,
                    FONT_NORMAL,
                    (90, 100, 115)
                )

            else:

                pygame.draw.rect(
                    SCREEN,
                    (20, 28, 42),
                    rect,
                    border_radius=3
                )

                pygame.draw.rect(
                    SCREEN,
                    GRID_COLOR,
                    rect,
                    width=1
                )


# =========================================================
# DRAW A* PATH
# =========================================================

def draw_astar_path():

    if not astar_path:
        return

    for index, position in enumerate(astar_path):

        if position == ai_position:
            continue

        if position == player_position:
            continue

        rect = cell_rect(position)

        overlay = pygame.Surface(
            (
                CELL_SIZE - 8,
                CELL_SIZE - 8
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (40, 220, 240, 65)
        )

        SCREEN.blit(
            overlay,
            (
                rect.x + 4,
                rect.y + 4
            )
        )

        pygame.draw.circle(
            SCREEN,
            CYAN,
            rect.center,
            4
        )


# =========================================================
# DRAW RANGE
# =========================================================

def draw_attack_range():

    if turn != "PLAYER":
        return

    if game_over:
        return

    for position in get_adjacent_positions(
        player_position
    ):

        if position in OBSTACLES:
            continue

        rect = cell_rect(
            position
        )

        pygame.draw.rect(
            SCREEN,
            (255, 205, 70, 35),
            rect,
            width=2,
            border_radius=5
        )


# =========================================================
# DRAW PLAYER
# =========================================================

def draw_fighter(position, team, defending=False):
    """Draw a compact top-down fighter instead of a simple circle."""
    center_x, center_y = cell_center(position)

    if team == "PLAYER":
        armor = BLUE
        accent = CYAN
        facing = 1
    else:
        armor = RED
        accent = ORANGE
        facing = -1

    # Soft shadow
    pygame.draw.ellipse(
        SCREEN,
        (5, 8, 15),
        pygame.Rect(
            center_x - 20,
            center_y + 13,
            40,
            9
        )
    )

    # Legs / boots
    pygame.draw.rect(
        SCREEN,
        (55, 62, 75),
        pygame.Rect(center_x - 12, center_y + 8, 8, 13),
        border_radius=3
    )
    pygame.draw.rect(
        SCREEN,
        (55, 62, 75),
        pygame.Rect(center_x + 4, center_y + 8, 8, 13),
        border_radius=3
    )

    # Body armor
    body = pygame.Rect(
        center_x - 14,
        center_y - 4,
        28,
        25
    )
    pygame.draw.rect(
        SCREEN,
        armor,
        body,
        border_radius=7
    )
    pygame.draw.rect(
        SCREEN,
        WHITE,
        body,
        width=1,
        border_radius=7
    )

    # Chest plate highlight
    pygame.draw.line(
        SCREEN,
        accent,
        (center_x, center_y - 1),
        (center_x, center_y + 16),
        width=3
    )

    # Helmet
    pygame.draw.circle(
        SCREEN,
        (205, 212, 222),
        (center_x, center_y - 12),
        11
    )
    pygame.draw.circle(
        SCREEN,
        armor,
        (center_x, center_y - 12),
        9
    )

    # Visor
    pygame.draw.rect(
        SCREEN,
        (25, 30, 40),
        pygame.Rect(center_x - 8, center_y - 14, 16, 5),
        border_radius=2
    )

    # Arms
    pygame.draw.line(
        SCREEN,
        armor,
        (center_x - 12, center_y + 2),
        (center_x - 20, center_y + 9),
        width=6
    )
    pygame.draw.line(
        SCREEN,
        armor,
        (center_x + 12, center_y + 2),
        (center_x + 20, center_y + 9),
        width=6
    )

    # Weapon
    sword_x = center_x + (24 * facing)
    pygame.draw.line(
        SCREEN,
        (210, 220, 230),
        (center_x + (13 * facing), center_y + 5),
        (sword_x, center_y - 8),
        width=4
    )
    pygame.draw.line(
        SCREEN,
        YELLOW,
        (center_x + (10 * facing), center_y + 3),
        (center_x + (15 * facing), center_y + 8),
        width=3
    )

    # Team badge
    badge = "P" if team == "PLAYER" else "A"
    draw_center_text(
        badge,
        (center_x, center_y - 12),
        FONT_SMALL,
        WHITE
    )

    # Active shield
    if defending:
        pygame.draw.circle(
            SCREEN,
            CYAN,
            (center_x, center_y),
            30,
            width=2
        )


def draw_player():
    draw_fighter(
        player_position,
        "PLAYER",
        player_defending
    )


# =========================================================
# DRAW AI
# =========================================================

def draw_ai():
    draw_fighter(
        ai_position,
        "AI",
        ai_defending
    )


# =========================================================
# DRAW SHIELD
# =========================================================

def draw_shield():

    global shield_animation

    if not shield_animation:
        return

    elapsed = (
        pygame.time.get_ticks()
        -
        shield_animation_start
    )

    if elapsed > 650:

        shield_animation = False

        return

    # The animation follows the unit that
    # actually pressed / chose DEFEND.

    if shield_owner == "PLAYER":

        center = cell_center(
            player_position
        )

    else:

        center = cell_center(
            ai_position
        )

    radius = 28 + int(
        4 * (elapsed / 650)
    )

    pygame.draw.circle(
        SCREEN,
        CYAN,
        center,
        radius,
        width=3
    )

    pygame.draw.circle(
        SCREEN,
        (100, 220, 255),
        center,
        radius - 6,
        width=1
    )


# =========================================================
# DRAW ATTACK ANIMATION
# =========================================================

def draw_attack_animation():

    global attack_animation

    if not attack_animation:
        return

    elapsed = (
        pygame.time.get_ticks()
        -
        attack_animation_start
    )

    duration = 300

    if elapsed > duration:

        attack_animation = False

        return

    if not attack_from or not attack_to:
        return

    start = cell_center(
        attack_from
    )

    end = cell_center(
        attack_to
    )

    progress = elapsed / duration

    current_x = (
        start[0]
        +
        (end[0] - start[0])
        * progress
    )

    current_y = (
        start[1]
        +
        (end[1] - start[1])
        * progress
    )

    current = (
        int(current_x),
        int(current_y)
    )

    pygame.draw.line(
        SCREEN,
        YELLOW,
        start,
        current,
        width=5
    )

    pygame.draw.circle(
        SCREEN,
        YELLOW,
        current,
        12
    )

    pygame.draw.circle(
        SCREEN,
        WHITE,
        current,
        5
    )


# =========================================================
# DRAW DAMAGE NUMBER
# =========================================================

def draw_damage_number():

    global damage_number

    if damage_number is None:
        return

    elapsed = (
        pygame.time.get_ticks()
        -
        damage_number_start
    )

    if elapsed > 900:

        damage_number = None

        return

    x, y = damage_number_position

    y -= int(
        elapsed * 0.04
    )

    alpha = max(
        0,
        255 - int(
            elapsed * 0.28
        )
    )

    text_surface = FONT_LARGE.render(
        f"-{damage_number}",
        True,
        YELLOW
    )

    text_surface.set_alpha(
        alpha
    )

    rect = text_surface.get_rect(
        center=(x, y)
    )

    SCREEN.blit(
        text_surface,
        rect
    )


# =========================================================
# ATTACK EFFECT
# =========================================================

def start_attack_animation(
    attacker,
    target,
    damage
):

    global attack_animation
    global attack_animation_start

    global attack_from
    global attack_to

    global damage_number
    global damage_number_start
    global damage_number_position

    attack_animation = True

    attack_animation_start = (
        pygame.time.get_ticks()
    )

    attack_from = attacker
    attack_to = target

    damage_number = damage

    damage_number_start = (
        pygame.time.get_ticks()
    )

    damage_number_position = cell_center(
        target
    )


# =========================================================
# DEFEND EFFECT
# =========================================================

def start_shield_animation(owner):

    global shield_animation
    global shield_animation_start
    global shield_owner

    shield_animation = True

    shield_animation_start = (
        pygame.time.get_ticks()
    )

    shield_owner = owner


# =========================================================
# PLAYER MOVE
# =========================================================

def move_player(
    dr,
    dc
):

    global player_position
    global player_defending

    if turn != "PLAYER":
        return

    if game_over:
        return

    new_position = (
        player_position[0] + dr,
        player_position[1] + dc
    )

    if not is_inside_grid(
        new_position
    ):
        return

    if new_position in OBSTACLES:
        add_log(
            "Cannot move through obstacle."
        )

        return

    if new_position == ai_position:

        add_log(
            "Cannot move onto AI."
        )

        return

    player_position = new_position

    add_log(
        f"Player moved to {player_position}."
    )

    # Moving drops the shield
    # (same rule as inside minimax.py).

    if player_defending:

        player_defending = False

        add_log(
            "Player lowered the shield."
        )

    end_player_turn()


# =========================================================
# PLAYER ATTACK
# =========================================================

def player_attack():

    global ai_hp
    global ai_defending
    global score
    global level

    if turn != "PLAYER":
        return

    if game_over:
        return

    if not can_attack(
        player_position,
        ai_position
    ):

        add_log(
            "AI is out of attack range."
        )

        return

    damage = PLAYER_DAMAGE

    if ai_defending:

        damage = int(
            damage * 0.5
        )

        ai_defending = False

        add_log(
            "AI shield reduced damage."
        )

    ai_hp = max(
        0,
        ai_hp - damage
    )

    level_before_attack = level

    # Reward accurate combat actions.
    score += damage

    start_attack_animation(
        player_position,
        ai_position,
        damage
    )

    add_log(
        f"Player attacked AI for {damage} damage."
    )

    check_game_over()

    if not game_over and level == level_before_attack:

        end_player_turn()


# =========================================================
# PLAYER DEFEND
# =========================================================

def player_defend():

    global player_defending

    if turn != "PLAYER":
        return

    if game_over:
        return

    player_defending = True

    start_shield_animation(
        "PLAYER"
    )

    add_log(
        "Player is defending."
    )

    end_player_turn()


# =========================================================
# END PLAYER TURN
# =========================================================

def end_player_turn():

    global turn
    global game_over
    global winner
    global ai_thinking
    global ai_turn_ready_time
    global player_turn_started_at

    if game_over:
        return

    turn = "AI"

    ai_thinking = True

    # The AI acts after a short delay.
    # The game loop keeps drawing during this time,
    # so animations and "AI THINKING..." stay visible.

    ai_turn_ready_time = (
        pygame.time.get_ticks()
        +
        AI_THINK_DELAY
    )


# =========================================================
# BUILD AI STATE
# =========================================================

def get_level_config():
    return LEVEL_CONFIG[level]


def get_ai_damage():
    return get_level_config()["damage"]


def get_ai_survival_threshold():
    return get_level_config()["survival_threshold"]


def get_ai_search_depth():
    return get_level_config()["depth"]


def build_ai_state():

    return {
        "ai_position": ai_position,
        "player_position": player_position,

        "ai_hp": ai_hp,
        "player_hp": player_hp,

        "ai_defending": ai_defending,
        "player_defending": player_defending,

        "rows": ROWS,
        "cols": COLS,

        "obstacles": set(OBSTACLES),
    }


# =========================================================
# FIND A* PATH
# =========================================================

def calculate_astar():

    global astar_path
    global astar_nodes
    global astar_path_cost
    global astar_time

    astar_path = []

    astar_nodes = 0
    astar_path_cost = 0
    astar_time = 0.0

    # Already in attack range:
    # no path is needed.

    if can_attack(
        ai_position,
        player_position
    ):
        return

    # AI needs to reach a cell adjacent
    # to the player, not player's cell.

    possible_goals = []

    for position in get_adjacent_positions(
        player_position
    ):

        if position in OBSTACLES:
            continue

        possible_goals.append(
            position
        )

    best_path = []
    total_nodes = 0

    start_time = time.perf_counter()

    # Player cell is treated as obstacle.

    path_obstacles = set(
        OBSTACLES
    )

    path_obstacles.add(
        player_position
    )

    for goal in possible_goals:

        path, nodes = a_star(
            ai_position,
            goal,
            ROWS,
            COLS,
            path_obstacles
        )

        # Count every node A* explored,
        # so Nodes and Time describe the same work.

        total_nodes += nodes

        if path:

            if not best_path:

                best_path = path

            elif len(path) < len(best_path):

                best_path = path

    end_time = time.perf_counter()

    astar_path = best_path

    astar_nodes = total_nodes

    if best_path:

        astar_path_cost = (
            len(best_path) - 1
        )

    else:

        astar_path_cost = 0

    astar_time = (
        end_time - start_time
    ) * 1000


# =========================================================
# A* NEXT STEP
# =========================================================

def get_astar_next_step():

    if len(astar_path) < 2:
        return None

    # Path normally starts at the AI's cell.

    if astar_path[0] == ai_position:
        return astar_path[1]

    # Safety: in case the path is reversed.

    if astar_path[-1] == ai_position:
        return astar_path[-2]

    return None


# =========================================================
# HYBRID DECISION (A* + MINIMAX)
# =========================================================

def get_safe_retreat_step():
    """
    Find a short, tactical retreat instead of sending the AI to the
    opposite side of the map. The AI tries to keep roughly 2-3 cells
    away from the player so the human can still chase and defeat it.
    """
    path_obstacles = set(OBSTACLES)
    path_obstacles.add(player_position)

    candidates = []

    for row in range(ROWS):
        for col in range(COLS):
            goal = (row, col)

            if goal in path_obstacles or goal == ai_position:
                continue

            distance = get_distance(goal, player_position)

            # Tactical retreat zone: far enough to avoid the next melee
            # hit, but not so far that the AI becomes impossible to catch.
            if distance < ATTACK_RANGE + 1 or distance > 3:
                continue

            path, nodes = a_star(
                ai_position,
                goal,
                ROWS,
                COLS,
                path_obstacles
            )

            if len(path) >= 2:
                candidates.append((
                    abs(distance - 2.5),
                    len(path) - 1,
                    path
                ))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[0][2][1]


def get_survival_action():
    """
    Decide what a critically wounded AI should do.

    First two survival turns: short retreat.
    After that: re-engage instead of endlessly running away.
    """
    if ai_hp > get_ai_survival_threshold():
        return None, False

    # If the AI has been hiding long enough, it must fight back.
    if ai_survival_turns > SURVIVAL_MAX_RETREAT_TURNS:
        if can_attack(ai_position, player_position):
            return "ATTACK", True

        # Not close enough to attack: take an A* step toward the player.
        path_obstacles = set(OBSTACLES)
        path_obstacles.add(player_position)

        path, _ = a_star(
            ai_position,
            player_position,
            ROWS,
            COLS,
            path_obstacles
        )

        if len(path) >= 2:
            next_step = path[1]
            if next_step not in OBSTACLES and next_step != player_position:
                return ("MOVE", next_step), True

    retreat_step = get_safe_retreat_step()

    if retreat_step is not None and ai_survival_turns <= SURVIVAL_MAX_RETREAT_TURNS:
        return ("MOVE", retreat_step), True

    # If there is no safe retreat, let Minimax decide.
    return None, False


def update_survival_state():
    """Update low-HP survival mode and apply prolonged-survival HP drain."""
    global ai_survival_mode
    global ai_survival_turns
    global ai_hp

    if ai_hp <= get_ai_survival_threshold() and ai_hp > 0:
        if not ai_survival_mode:
            ai_survival_mode = True
            ai_survival_turns = 0
            add_log("AI entered SURVIVAL MODE — it is critically wounded.")

        ai_survival_turns += 1

        if ai_survival_turns > SURVIVAL_MAX_RETREAT_TURNS:
            ai_hp = max(0, ai_hp - SURVIVAL_HP_DRAIN)
            add_log(
                f"AI is losing {SURVIVAL_HP_DRAIN} HP from prolonged survival mode."
            )

    elif ai_hp > get_ai_survival_threshold() and ai_survival_mode:
        ai_survival_mode = False
        ai_survival_turns = 0
        add_log("AI recovered enough HP and left survival mode.")


def apply_low_hp_retreat(action):
    """Use temporary survival behavior without making the AI permanently flee."""
    survival_action, used_survival = get_survival_action()

    if survival_action is not None:
        return survival_action, used_survival

    return action, False


def apply_astar_guidance(action):

    # Returns: (final_action, used_astar)

    if not USE_ASTAR_MOVEMENT:
        return action, False

    # In attack range: Minimax decides.

    if can_attack(
        ai_position,
        player_position
    ):
        return action, False

    next_step = get_astar_next_step()

    if next_step is None:
        return action, False

    if next_step in OBSTACLES:
        return action, False

    if next_step == player_position:
        return action, False

    # Safety rule: if one player hit can kill the AI,
    # do not walk into the player's attack range.
    # Keep Minimax's (careful) decision instead.

    if (
        ai_hp <= PLAYER_DAMAGE
        and
        can_attack(next_step, player_position)
    ):
        return action, False

    return (
        ("MOVE", next_step),
        True
    )


# =========================================================
# APPLY AI ACTION
# =========================================================

def execute_ai_action(
    action
):

    global ai_position
    global player_hp
    global ai_hp
    global player_defending
    global ai_defending
    global ai_survival_mode
    global ai_survival_turns

    global ai_action_text

    # -----------------------------------------------------
    # ATTACK
    # -----------------------------------------------------

    if action == "ATTACK":

        if not can_attack(
            ai_position,
            player_position
        ):

            add_log(
                "AI tried to attack but player is out of range."
            )

            return

        damage = get_ai_damage()

        if player_defending:

            damage = int(
                damage * 0.5
            )

            player_defending = False

            add_log(
                "Player shield reduced AI damage."
            )

        player_hp = max(
            0,
            player_hp - damage
        )

        start_attack_animation(
            ai_position,
            player_position,
            damage
        )

        add_log(
            f"AI attacked Player for {damage} damage."
        )

        # Successful attacks give the wounded fighter a small recovery.
        # This is deliberately limited so the AI cannot heal indefinitely.
        if ai_survival_mode:
            old_hp = ai_hp
            ai_hp = min(
                ai_max_hp,
                ai_hp + (SURVIVAL_ATTACK_HEAL + max(0, level - 4) * 2)
            )
            healed = ai_hp - old_hp

            if healed > 0:
                add_log(
                    f"AI recovered +{healed} HP from a successful counterattack."
                )

            if ai_hp > get_ai_survival_threshold():
                ai_survival_mode = False
                ai_survival_turns = 0
                add_log("AI left survival mode and returned to normal combat.")

    # -----------------------------------------------------
    # DEFEND
    # -----------------------------------------------------

    elif action == "DEFEND":

        ai_defending = True

        start_shield_animation(
            "AI"
        )

        add_log(
            "AI is defending."
        )

    # -----------------------------------------------------
    # MOVE
    # -----------------------------------------------------

    elif (
        isinstance(action, tuple)
        and
        action[0] == "MOVE"
    ):

        new_position = action[1]

        if new_position in OBSTACLES:

            add_log(
                "AI cannot move through obstacle."
            )

            return

        if new_position == player_position:

            add_log(
                "AI cannot move onto Player."
            )

            return

        if is_inside_grid(
            new_position
        ):

            ai_position = new_position

            add_log(
                f"AI moved to {ai_position}."
            )

            # Moving drops the shield
            # (same rule as inside minimax.py).

            if ai_defending:

                ai_defending = False

                add_log(
                    "AI lowered its shield."
                )


# =========================================================
# AI TURN
# =========================================================

def run_ai_turn():

    global turn
    global ai_thinking

    global ai_action_text
    global player_turn_started_at
    global ai_survival_mode
    global ai_survival_turns

    global minimax_nodes
    global minimax_pruned
    global minimax_time
    global minimax_score

    if game_over:
        return

    # -----------------------------------------------------
    # SURVIVAL MODE UPDATE
    # -----------------------------------------------------

    update_survival_state()

    # Prolonged survival mode can drain the last HP.
    if ai_hp <= 0:
        check_game_over()
        return

    # -----------------------------------------------------
    # A* SEARCH
    # -----------------------------------------------------

    calculate_astar()

    # -----------------------------------------------------
    # MINIMAX
    # -----------------------------------------------------

    state = build_ai_state()

    start_time = time.perf_counter()

    (
        best_action,
        best_score,
        nodes,
        pruned
    ) = get_best_action(
        state,
        depth=get_ai_search_depth()
    )

    end_time = time.perf_counter()

    minimax_time = (
        end_time - start_time
    ) * 1000

    minimax_nodes = nodes
    minimax_pruned = pruned
    minimax_score = best_score

    # -----------------------------------------------------
    # CRITICAL HP: retreat before the player can finish AI
    # -----------------------------------------------------

    final_action, used_retreat = apply_low_hp_retreat(
        best_action
    )

    # -----------------------------------------------------
    # HYBRID: A* chooses the approach step when far away
    # -----------------------------------------------------

    if used_retreat:
        used_astar = False
    else:
        final_action, used_astar = apply_astar_guidance(
            best_action
        )

    ai_action_text = format_ai_action(
        final_action,
        used_astar,
        used_retreat
    )

    # -----------------------------------------------------
    # EXECUTE ACTION
    # -----------------------------------------------------

    execute_ai_action(
        final_action
    )

    check_game_over()

    if not game_over:

        turn = "PLAYER"

        ai_thinking = False
        player_turn_started_at = pygame.time.get_ticks()

        add_log(
            f"Your turn. Response window: {PLAYER_RESPONSE_TIME // 1000}s."
        )


# =========================================================
# FORMAT AI ACTION
# =========================================================

def format_ai_action(
    action,
    used_astar=False,
    used_retreat=False
):

    if action == "ATTACK":

        return "ATTACK"

    if action == "DEFEND":

        return "DEFEND"

    if (
        isinstance(action, tuple)
        and
        action[0] == "MOVE"
    ):

        text = (
            f"MOVE → {action[1]}"
        )

        if used_retreat:

            text += " (RETREAT)"

        elif used_astar:

            text += " (A*)"

        return text

    return str(action)


# =========================================================
# GAME OVER
# =========================================================

def start_next_level():
    """Advance from one fighter to the next stage without resetting score."""
    global level
    global ai_max_hp
    global ai_hp
    global player_hp
    global player_position
    global ai_position
    global player_defending
    global ai_defending
    global turn
    global game_over
    global winner
    global ai_thinking
    global ai_turn_ready_time
    global player_turn_started_at
    global ai_action_text
    global attack_animation
    global damage_number
    global shield_animation
    global shield_owner
    global ai_survival_mode
    global ai_survival_turns
    global ai_name

    level += 1
    config = LEVEL_CONFIG[level]
    ai_name = config["name"]

    game_over = False
    winner = None
    ai_max_hp = config["hp"]
    ai_hp = ai_max_hp

    # Fresh player life for each stage keeps progression fair.
    player_hp = MAX_HP

    player_position = (2, 2)
    ai_position = (5, 9)

    player_defending = False
    ai_defending = False

    turn = "PLAYER"
    ai_thinking = False
    ai_turn_ready_time = 0
    player_turn_started_at = pygame.time.get_ticks()
    ai_action_text = "New opponent"

    ai_survival_mode = False
    ai_survival_turns = 0

    attack_animation = False
    damage_number = None
    shield_animation = False
    shield_owner = None

    add_log(
        f"LEVEL {level} — {ai_name} enters the arena!"
    )
    add_log(
        f"Enemy HP: {ai_max_hp}  |  Damage: {config['damage']}  |  Search Depth: {config['depth']}"
    )
    add_log(
        "Your turn. Defeat this fighter to advance."
    )


def check_game_over():

    global game_over
    global winner
    global ai_thinking
    global score
    global final_victory

    if player_hp <= 0:

        game_over = True
        winner = "AI"
        final_victory = False
        ai_thinking = False

        add_log(
            f"{ai_name} wins. Final score: {score}."
        )

        return

    if ai_hp <= 0:

        reward = LEVEL_CONFIG[level]["reward"]
        score += reward

        if level >= FINAL_LEVEL:
            # Final boss defeated: this is the real end of the game.
            game_over = True
            winner = "PLAYER"
            final_victory = True
            ai_thinking = False

            add_log(
                f"FINAL BOSS DEFEATED! +{reward} score."
            )
            add_log(
                f"🏆 ARENA CLEARED! Final score: {score}."
            )

            return

        add_log(
            f"{ai_name} DEFEATED! +{reward} score."
        )
        add_log(
            f"Preparing Level {level + 1}..."
        )

        start_next_level()


# =========================================================
# AI BRAIN PANEL
# =========================================================

def draw_ai_brain_panel():

    rect = pygame.Rect(
        735,
        90,
        420,
        340
    )

    draw_panel(
        rect,
        "AI BRAIN"
    )

    y = rect.y + 55

    draw_text(
        "Algorithms",
        (rect.x + 18, y),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        "A* + Minimax",
        (rect.x + 180, y),
        FONT_NORMAL,
        CYAN
    )

    y += 30

    draw_text(
        "Alpha-Beta",
        (rect.x + 18, y),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        "Enabled",
        (rect.x + 180, y),
        FONT_NORMAL,
        GREEN
    )

    y += 30

    draw_text(
        "Search Depth",
        (rect.x + 18, y),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        str(get_ai_search_depth()),
        (rect.x + 180, y),
        FONT_NORMAL,
        WHITE
    )

    y += 30

    draw_text(
        "Current Action",
        (rect.x + 18, y),
        FONT_SMALL,
        GRAY
    )

    draw_text(
        ai_action_text,
        (rect.x + 180, y),
        FONT_NORMAL,
        YELLOW
    )

    y += 28

    survival_text = (
        f"SURVIVAL {ai_survival_turns}/{SURVIVAL_MAX_RETREAT_TURNS}"
        if ai_survival_mode
        else "NORMAL COMBAT"
    )
    survival_color = ORANGE if ai_survival_mode else GRAY

    draw_text(
        survival_text,
        (rect.x + 180, y),
        FONT_SMALL,
        survival_color
    )

    y += 35

    # A* section

    draw_text(
        "A* Search",
        (rect.x + 18, y),
        FONT_MEDIUM,
        CYAN
    )

    y += 28

    draw_text(
        f"Nodes: {astar_nodes}",
        (rect.x + 18, y),
        FONT_SMALL,
        WHITE
    )

    draw_text(
        f"Path Cost: {astar_path_cost}",
        (rect.x + 190, y),
        FONT_SMALL,
        WHITE
    )

    y += 25

    draw_text(
        f"Time: {astar_time:.3f} ms",
        (rect.x + 18, y),
        FONT_SMALL,
        WHITE
    )

    y += 32

    # Minimax section

    draw_text(
        "Minimax + Alpha-Beta",
        (rect.x + 18, y),
        FONT_MEDIUM,
        PURPLE
    )

    y += 28

    draw_text(
        f"Nodes: {minimax_nodes}",
        (rect.x + 18, y),
        FONT_SMALL,
        WHITE
    )

    draw_text(
        f"Pruned: {minimax_pruned}",
        (rect.x + 190, y),
        FONT_SMALL,
        GREEN
    )

    y += 25

    draw_text(
        f"Time: {minimax_time:.3f} ms",
        (rect.x + 18, y),
        FONT_SMALL,
        WHITE
    )

    draw_text(
        f"Score: {minimax_score}",
        (rect.x + 190, y),
        FONT_SMALL,
        WHITE
    )


# =========================================================
# BATTLE LOG
# =========================================================

def draw_battle_log():

    rect = pygame.Rect(
        735,
        440,
        420,
        165
    )

    draw_panel(
        rect,
        "BATTLE LOG"
    )

    y = rect.y + 48

    for message in battle_log:

        draw_text(
            "• " + message,
            (
                rect.x + 15,
                y
            ),
            FONT_SMALL,
            GRAY
        )

        y += 17

        if y > rect.bottom - 15:
            break


# =========================================================
# TOP BAR
# =========================================================

def draw_top_bar():

    draw_text(
        "AI BATTLE ARENA  •  FIGHTER MODE",
        (45, 25),
        FONT_TITLE,
        WHITE
    )

    draw_text(
        "A* Pathfinding  •  Minimax  •  Alpha-Beta",
        (48, 67),
        FONT_SMALL,
        GRAY
    )

    stage_text = f"LEVEL {level}/5  •  {ai_name}"
    stage_color = YELLOW if level == FINAL_LEVEL else CYAN
    draw_text(
        stage_text,
        (300, 67),
        FONT_SMALL,
        stage_color
    )

    # Turn indicator

    if game_over:

        turn_text = (
            f"{winner} WINS"
        )

        turn_color = YELLOW

    elif ai_thinking:

        turn_text = "AI THINKING..."

        turn_color = PURPLE

    elif turn == "PLAYER":

        turn_text = "YOUR TURN"

        turn_color = CYAN

    else:

        turn_text = "AI TURN"

        turn_color = RED

    draw_center_text(
        turn_text,
        (960, 48),
        FONT_MEDIUM,
        turn_color
    )


# =========================================================
# PLAYER / AI STATUS
# =========================================================

def draw_status_panel():

    rect = pygame.Rect(
        45,
        610,
        1110,
        75
    )

    draw_panel(rect)

    draw_hp_bar(
        65,
        640,
        210,
        14,
        player_hp,
        MAX_HP,
        "PLAYER",
        BLUE
    )

    draw_hp_bar(
        300,
        640,
        210,
        14,
        ai_hp,
        ai_max_hp,
        f"{ai_name} • LV {level}",
        RED
    )

    draw_text(
        f"SCORE  {score}",
        (535, 625),
        FONT_MEDIUM,
        YELLOW
    )

    # Response timer
    if turn == "PLAYER" and not game_over:
        elapsed = pygame.time.get_ticks() - player_turn_started_at
        remaining = max(
            0,
            (PLAYER_RESPONSE_TIME - elapsed) / 1000
        )
        timer_color = GREEN if remaining > 3 else ORANGE
        draw_text(
            f"TIME  {remaining:04.1f}s",
            (535, 650),
            FONT_SMALL,
            timer_color
        )

    draw_text(
        "WASD / Arrows",
        (665, 615),
        FONT_SMALL,
        GRAY
    )
    draw_text(
        "Move",
        (665, 635),
        FONT_NORMAL,
        WHITE
    )

    draw_text(
        "SPACE",
        (765, 615),
        FONT_SMALL,
        GRAY
    )
    draw_text(
        "Attack",
        (765, 635),
        FONT_NORMAL,
        WHITE
    )

    draw_text(
        "F",
        (855, 615),
        FONT_SMALL,
        GRAY
    )
    draw_text(
        "Defend",
        (855, 635),
        FONT_NORMAL,
        WHITE
    )

    draw_text(
        "R",
        (930, 615),
        FONT_SMALL,
        GRAY
    )
    draw_text(
        "Restart",
        (930, 635),
        FONT_NORMAL,
        WHITE
    )


# =========================================================
# GAME OVER OVERLAY
# =========================================================

def draw_game_over():

    if not game_over:
        return

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 170)
    )

    SCREEN.blit(
        overlay,
        (0, 0)
    )

    center_x = WIDTH // 2
    center_y = HEIGHT // 2

    if final_victory:
        title = "🏆 ARENA CLEARED!"
        title_color = YELLOW
        subtitle = "FINAL BOSS DEFEATED — YOU ARE THE CHAMPION"
    else:
        title = "RUN OVER"
        title_color = RED
        subtitle = f"Defeated by {ai_name}"

    draw_center_text(
        title,
        (
            center_x,
            center_y - 65
        ),
        FONT_TITLE,
        title_color
    )

    draw_center_text(
        subtitle,
        (
            center_x,
            center_y - 20
        ),
        FONT_NORMAL,
        WHITE
    )

    draw_center_text(
        f"Final Score: {score}  •  Level {level}/5",
        (
            center_x,
            center_y + 15
        ),
        FONT_MEDIUM,
        YELLOW if final_victory else WHITE
    )

    draw_center_text(
        "Press R to play again",
        (
            center_x,
            center_y + 55
        ),
        FONT_NORMAL,
        GRAY
    )


# =========================================================
# DRAW ALL
# =========================================================

def draw():

    SCREEN.fill(
        BG_COLOR
    )

    # Top

    draw_top_bar()

    # Main battlefield panel

    battlefield_rect = pygame.Rect(
        25,
        90,
        680,
        480
    )

    draw_panel(
        battlefield_rect,
        "BATTLEFIELD"
    )

    # Grid

    draw_grid()

    draw_attack_range()

    draw_astar_path()

    draw_player()

    draw_ai()

    draw_attack_animation()

    draw_shield()

    draw_damage_number()

    # Right panels

    draw_ai_brain_panel()

    draw_battle_log()

    # Bottom

    draw_status_panel()

    # Game over

    draw_game_over()

    pygame.display.flip()


# =========================================================
# KEYBOARD HANDLING
# =========================================================

def handle_keydown(event):

    if event.key == pygame.K_ESCAPE:

        pygame.quit()

        sys.exit()

    if event.key == pygame.K_r:

        reset_game()

        return

    if game_over:
        return

    if turn != "PLAYER":
        return

    # -----------------------------------------------------
    # MOVEMENT
    # -----------------------------------------------------

    if event.key in (
        pygame.K_w,
        pygame.K_UP
    ):

        move_player(
            -1,
            0
        )

    elif event.key in (
        pygame.K_s,
        pygame.K_DOWN
    ):

        move_player(
            1,
            0
        )

    elif event.key in (
        pygame.K_a,
        pygame.K_LEFT
    ):

        move_player(
            0,
            -1
        )

    elif event.key in (
        pygame.K_d,
        pygame.K_RIGHT
    ):

        move_player(
            0,
            1
        )

    # -----------------------------------------------------
    # ATTACK
    # -----------------------------------------------------

    elif event.key == pygame.K_SPACE:

        player_attack()

    # -----------------------------------------------------
    # DEFEND
    # -----------------------------------------------------

    elif event.key == pygame.K_f:

        player_defend()


def check_player_response_timeout():
    """Auto-defend if the player takes too long to choose an action."""
    if game_over or turn != "PLAYER" or ai_thinking:
        return

    elapsed = pygame.time.get_ticks() - player_turn_started_at

    if elapsed >= PLAYER_RESPONSE_TIME:
        add_log("Response time expired — Player auto-defends.")
        player_defend()


# =========================================================
# MAIN LOOP
# =========================================================

def main():

    reset_game()

    running = True

    while running:

        # -------------------------------------------------
        # EVENTS
        # -------------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.KEYDOWN:

                handle_keydown(
                    event
                )

        # -------------------------------------------------
        # PLAYER RESPONSE TIMER
        # -------------------------------------------------

        check_player_response_timeout()

        # -------------------------------------------------
        # AI TURN
        #
        # No blocking delay here. The AI simply waits
        # until ai_turn_ready_time while the screen
        # keeps updating.
        # -------------------------------------------------

        if (
            turn == "AI"
            and
            ai_thinking
            and
            not game_over
            and
            pygame.time.get_ticks() >= ai_turn_ready_time
        ):

            run_ai_turn()

        # -------------------------------------------------
        # DRAW
        # -------------------------------------------------

        draw()

        CLOCK.tick(60)

    pygame.quit()

    sys.exit()


# =========================================================
# PROGRAM START
# =========================================================

if __name__ == "__main__":

    main()