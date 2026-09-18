# =========================================================
# AI BATTLE ARENA
# MINIMAX + ALPHA-BETA PRUNING
# =========================================================


# =========================================================
# GAME CONSTANTS
# =========================================================

PLAYER_DAMAGE = 20
AI_DAMAGE = 15

ATTACK_RANGE = 1

DEFEND_REDUCTION = 0.5


# =========================================================
# DISTANCE
# =========================================================

def get_distance(
    position_a,
    position_b
):

    row_a, col_a = position_a
    row_b, col_b = position_b

    return (
        abs(row_a - row_b)
        +
        abs(col_a - col_b)
    )


# =========================================================
# CAN ATTACK
# =========================================================

def can_attack(
    attacker_position,
    target_position
):

    return (
        get_distance(
            attacker_position,
            target_position
        )
        <= ATTACK_RANGE
    )


# =========================================================
# VALID POSITION
# =========================================================

def is_valid_position(
    position,
    rows,
    cols,
    obstacles,
    player_position
):

    row, col = position

    # Grid boundary

    if row < 0 or row >= rows:
        return False

    if col < 0 or col >= cols:
        return False

    # Obstacle

    if position in obstacles:
        return False

    # Cannot move onto player

    if position == player_position:
        return False

    return True


# =========================================================
# GET VALID MOVES
# =========================================================

def get_valid_moves(state):

    ai_position = state["ai_position"]

    player_position = state["player_position"]

    rows = state.get(
        "rows",
        8
    )

    cols = state.get(
        "cols",
        12
    )

    obstacles = state.get(
        "obstacles",
        set()
    )

    row, col = ai_position

    directions = [

        (-1, 0),   # UP

        (1, 0),    # DOWN

        (0, -1),   # LEFT

        (0, 1),    # RIGHT

    ]

    valid_moves = []

    for row_change, col_change in directions:

        new_position = (

            row + row_change,

            col + col_change

        )

        if is_valid_position(
            new_position,
            rows,
            cols,
            obstacles,
            player_position
        ):

            valid_moves.append(
                new_position
            )

    return valid_moves


# =========================================================
# POSSIBLE AI ACTIONS
# =========================================================

def get_possible_actions(state):

    actions = []

    ai_position = state["ai_position"]

    player_position = state["player_position"]

    distance = get_distance(
        ai_position,
        player_position
    )

    # -----------------------------------------------------
    # ATTACK
    # -----------------------------------------------------

    if distance <= ATTACK_RANGE:

        actions.append(
            "ATTACK"
        )

    # -----------------------------------------------------
    # DEFEND
    # -----------------------------------------------------

    actions.append(
        "DEFEND"
    )

    # -----------------------------------------------------
    # MOVE
    # -----------------------------------------------------

    valid_moves = get_valid_moves(
        state
    )

    for position in valid_moves:

        actions.append(
            (
                "MOVE",
                position
            )
        )

    return actions


# =========================================================
# EVALUATION FUNCTION
# =========================================================

def evaluate(state):

    ai_hp = state["ai_hp"]

    player_hp = state["player_hp"]

    ai_position = state["ai_position"]

    player_position = state["player_position"]

    ai_defending = state.get(
        "ai_defending",
        False
    )

    player_defending = state.get(
        "player_defending",
        False
    )

    # =====================================================
    # TERMINAL STATES
    # =====================================================

    if player_hp <= 0:

        return 10000

    if ai_hp <= 0:

        return -10000

    # =====================================================
    # BASIC HP ADVANTAGE
    # =====================================================

    score = (
        ai_hp
        -
        player_hp
    )

    # =====================================================
    # DISTANCE
    # =====================================================

    distance = get_distance(
        ai_position,
        player_position
    )

    # Close distance is useful for AI

    if distance == 1:

        score += 25

    elif distance == 2:

        score += 12

    elif distance == 3:

        score += 5

    else:

        score -= min(
            distance,
            10
        )

    # =====================================================
    # AGGRESSION BONUS
    # =====================================================

    # If player has low HP,
    # AI should prefer finishing the fight.

    if player_hp <= 30:

        score += 30

    elif player_hp <= 50:

        score += 15

    # =====================================================
    # AI HEALTH CONDITION
    # =====================================================

    # If AI is badly damaged,
    # defensive position becomes more valuable.

    if ai_hp <= 30:

        score -= 20

    elif ai_hp <= 50:

        score -= 5

    # =====================================================
    # DEFENSE BONUS
    # =====================================================

    # Small bonus only.
    #
    # Previously this was +15,
    # which made DEFEND too powerful.

    if ai_defending:

        score += 5

    # =====================================================
    # PLAYER DEFENDING
    # =====================================================

    if player_defending:

        score -= 5

    # =====================================================
    # ATTACKING POSITION BONUS
    # =====================================================

    if distance == 1:

        # Being in attack range is highly valuable.

        score += 10

    return score


# =========================================================
# APPLY AI ACTION
# =========================================================

def apply_ai_action(
    state,
    action
):

    new_state = state.copy()

    # Preserve values

    new_state["ai_position"] = (
        state["ai_position"]
    )

    new_state["ai_defending"] = (
        state.get(
            "ai_defending",
            False
        )
    )

    new_state["player_defending"] = (
        state.get(
            "player_defending",
            False
        )
    )

    # =====================================================
    # ATTACK
    # =====================================================

    if action == "ATTACK":

        if can_attack(
            state["ai_position"],
            state["player_position"]
        ):

            damage = AI_DAMAGE

            # Player defending

            if state.get(
                "player_defending",
                False
            ):

                damage = int(
                    damage
                    *
                    DEFEND_REDUCTION
                )

            new_state["player_hp"] = max(

                0,

                state["player_hp"]
                -
                damage

            )

            # Player's defense is consumed

            new_state["player_defending"] = False

    # =====================================================
    # DEFEND
    # =====================================================

    elif action == "DEFEND":

        new_state["ai_defending"] = True

    # =====================================================
    # MOVE
    # =====================================================

    elif (
        isinstance(action, tuple)
        and
        action[0] == "MOVE"
    ):

        new_position = action[1]

        valid_moves = get_valid_moves(
            state
        )

        if new_position in valid_moves:

            new_state["ai_position"] = (
                new_position
            )

        # Moving means AI is no longer
        # actively defending.

        new_state["ai_defending"] = False

    return new_state


# =========================================================
# APPLY PLAYER ACTION
# =========================================================

def apply_player_action(
    state,
    action
):

    new_state = state.copy()

    new_state["ai_defending"] = (
        state.get(
            "ai_defending",
            False
        )
    )

    new_state["player_defending"] = (
        state.get(
            "player_defending",
            False
        )
    )

    # =====================================================
    # PLAYER ATTACK
    # =====================================================

    if action == "ATTACK":

        if can_attack(
            state["player_position"],
            state["ai_position"]
        ):

            damage = PLAYER_DAMAGE

            # AI defending

            if state.get(
                "ai_defending",
                False
            ):

                damage = int(
                    damage
                    *
                    DEFEND_REDUCTION
                )

            new_state["ai_hp"] = max(

                0,

                state["ai_hp"]
                -
                damage

            )

            # AI defense is consumed

            new_state["ai_defending"] = False

    # =====================================================
    # PLAYER DEFEND
    # =====================================================

    elif action == "DEFEND":

        new_state["player_defending"] = True

    return new_state


# =========================================================
# MINIMAX
# =========================================================

def minimax(
    state,
    depth,
    maximizing_player,
    alpha,
    beta,
    stats
):

    stats["nodes"] += 1

    # =====================================================
    # TERMINAL CONDITION
    # =====================================================

    if depth == 0:

        return evaluate(
            state
        )

    if state["ai_hp"] <= 0:

        return evaluate(
            state
        )

    if state["player_hp"] <= 0:

        return evaluate(
            state
        )

    # =====================================================
    # AI MAXIMIZING PLAYER
    # =====================================================

    if maximizing_player:

        best_score = float(
            "-inf"
        )

        actions = get_possible_actions(
            state
        )

        if not actions:

            return evaluate(
                state
            )

        for action in actions:

            new_state = apply_ai_action(
                state,
                action
            )

            score = minimax(

                new_state,

                depth - 1,

                False,

                alpha,

                beta,

                stats

            )

            best_score = max(
                best_score,
                score
            )

            alpha = max(
                alpha,
                best_score
            )

            # =================================================
            # ALPHA-BETA PRUNING
            # =================================================

            if beta <= alpha:

                stats["pruned"] += 1

                break

        return best_score

    # =====================================================
    # PLAYER MINIMIZING PLAYER
    # =====================================================

    else:

        best_score = float(
            "inf"
        )

        # -------------------------------------------------
        # Player can attack or defend
        # -------------------------------------------------

        player_actions = [

            "ATTACK",

            "DEFEND"

        ]

        for action in player_actions:

            new_state = apply_player_action(

                state,

                action

            )

            score = minimax(

                new_state,

                depth - 1,

                True,

                alpha,

                beta,

                stats

            )

            best_score = min(

                best_score,

                score

            )

            beta = min(

                beta,

                best_score

            )

            # =================================================
            # ALPHA-BETA PRUNING
            # =================================================

            if beta <= alpha:

                stats["pruned"] += 1

                break

        return best_score


# =========================================================
# GET BEST AI ACTION
# =========================================================

def get_best_action(
    state,
    depth=3
):

    actions = get_possible_actions(
        state
    )

    if not actions:

        return (

            "DEFEND",

            0,

            0,

            0

        )

    best_action = actions[0]

    best_score = float(
        "-inf"
    )

    stats = {

        "nodes": 0,

        "pruned": 0

    }

    # =====================================================
    # TEST EACH POSSIBLE ACTION
    # =====================================================

    for action in actions:

        new_state = apply_ai_action(

            state,

            action

        )

        score = minimax(

            new_state,

            depth - 1,

            False,

            float("-inf"),

            float("inf"),

            stats

        )

        # -------------------------------------------------
        # Select highest score
        # -------------------------------------------------

        if score > best_score:

            best_score = score

            best_action = action

    return (

        best_action,

        best_score,

        stats["nodes"],

        stats["pruned"]

    )