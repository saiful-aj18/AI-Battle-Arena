# =========================================================
# AI BATTLE ARENA
# MINIMAX + ALPHA-BETA PRUNING
# =========================================================


# =========================================================
# CONSTANTS
# =========================================================

ATTACK_DAMAGE = 15

DEFEND_REDUCTION = 0.5

ATTACK_RANGE = 1


# =========================================================
# DISTANCE
# =========================================================

def get_distance(ai_position, player_position):

    return (
        abs(ai_position[0] - player_position[0])
        +
        abs(ai_position[1] - player_position[1])
    )


# =========================================================
# CHECK ATTACK RANGE
# =========================================================

def can_attack(ai_position, player_position):

    distance = get_distance(
        ai_position,
        player_position
    )

    return distance <= ATTACK_RANGE


# =========================================================
# GENERATE POSSIBLE ACTIONS
# =========================================================

def get_possible_actions(
    ai_position,
    player_position
):

    actions = [
        "ATTACK",
        "DEFEND",
        "MOVE"
    ]

    # If AI is not close enough,
    # attacking is not possible.

    if not can_attack(
        ai_position,
        player_position
    ):

        actions.remove("ATTACK")

    return actions


# =========================================================
# EVALUATION FUNCTION
# =========================================================

def evaluate_state(state):

    ai_hp = state["ai_hp"]

    player_hp = state["player_hp"]

    ai_position = state["ai_position"]

    player_position = state["player_position"]

    ai_defending = state["ai_defending"]

    distance = get_distance(
        ai_position,
        player_position
    )

    # =====================================================
    # TERMINAL STATES
    # =====================================================

    if player_hp <= 0:

        return 1000

    if ai_hp <= 0:

        return -1000

    # =====================================================
    # BASIC HP ADVANTAGE
    # =====================================================

    score = (
        ai_hp
        -
        player_hp
    )

    # =====================================================
    # DISTANCE BONUS
    # =====================================================

    if distance == 1:

        score += 20

    elif distance == 2:

        score += 10

    elif distance == 3:

        score += 5

    # =====================================================
    # DEFENSE BONUS
    # =====================================================

    if ai_defending:

        score += 15

    return score


# =========================================================
# APPLY AI ACTION
# =========================================================

def apply_action(
    state,
    action
):

    new_state = {

        "ai_hp": state["ai_hp"],

        "player_hp": state["player_hp"],

        "ai_position": list(
            state["ai_position"]
        ),

        "player_position": list(
            state["player_position"]
        ),

        "ai_defending":
            state["ai_defending"],

        "player_defending":
            state["player_defending"]
    }

    # =====================================================
    # ATTACK
    # =====================================================

    if action == "ATTACK":

        if can_attack(
            new_state["ai_position"],
            new_state["player_position"]
        ):

            damage = ATTACK_DAMAGE

            if new_state["player_defending"]:

                damage = int(
                    damage
                    *
                    DEFEND_REDUCTION
                )

                new_state[
                    "player_defending"
                ] = False

            new_state["player_hp"] = max(
                0,
                new_state["player_hp"]
                -
                damage
            )

    # =====================================================
    # DEFEND
    # =====================================================

    elif action == "DEFEND":

        new_state[
            "ai_defending"
        ] = True

    # =====================================================
    # MOVE
    # =====================================================

    elif action == "MOVE":

        ai_row, ai_col = (
            new_state["ai_position"]
        )

        player_row, player_col = (
            new_state["player_position"]
        )

        # Move one step toward player

        row_difference = (
            player_row - ai_row
        )

        col_difference = (
            player_col - ai_col
        )

        if abs(row_difference) >= abs(
            col_difference
        ):

            if row_difference > 0:

                ai_row += 1

            elif row_difference < 0:

                ai_row -= 1

        else:

            if col_difference > 0:

                ai_col += 1

            elif col_difference < 0:

                ai_col -= 1

        new_state["ai_position"] = [
            ai_row,
            ai_col
        ]

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
    nodes
):

    nodes[0] += 1

    # =====================================================
    # TERMINAL CONDITION
    # =====================================================

    if depth == 0:

        return evaluate_state(
            state
        )

    if state["player_hp"] <= 0:

        return evaluate_state(
            state
        )

    if state["ai_hp"] <= 0:

        return evaluate_state(
            state
        )

    # =====================================================
    # AI MAXIMIZING
    # =====================================================

    if maximizing_player:

        max_evaluation = float("-inf")

        actions = get_possible_actions(
            state["ai_position"],
            state["player_position"]
        )

        for action in actions:

            new_state = apply_action(
                state,
                action
            )

            evaluation = minimax(
                new_state,
                depth - 1,
                False,
                alpha,
                beta,
                nodes
            )

            max_evaluation = max(
                max_evaluation,
                evaluation
            )

            alpha = max(
                alpha,
                evaluation
            )

            # =================================================
            # ALPHA-BETA PRUNING
            # =================================================

            if beta <= alpha:

                break

        return max_evaluation

    # =====================================================
    # PLAYER MINIMIZING
    # =====================================================

    else:

        min_evaluation = float("inf")

        actions = [
            "ATTACK",
            "DEFEND"
        ]

        for action in actions:

            new_state = {

                "ai_hp":
                    state["ai_hp"],

                "player_hp":
                    state["player_hp"],

                "ai_position":
                    list(
                        state["ai_position"]
                    ),

                "player_position":
                    list(
                        state["player_position"]
                    ),

                "ai_defending":
                    state["ai_defending"],

                "player_defending":
                    state["player_defending"]
            }

            if action == "ATTACK":

                if can_attack(
                    new_state["ai_position"],
                    new_state["player_position"]
                ):

                    damage = 20

                    if new_state[
                        "ai_defending"
                    ]:

                        damage //= 2

                    new_state[
                        "ai_hp"
                    ] = max(
                        0,
                        new_state["ai_hp"]
                        -
                        damage
                    )

            elif action == "DEFEND":

                new_state[
                    "player_defending"
                ] = True

            evaluation = minimax(
                new_state,
                depth - 1,
                True,
                alpha,
                beta,
                nodes
            )

            min_evaluation = min(
                min_evaluation,
                evaluation
            )

            beta = min(
                beta,
                evaluation
            )

            # =================================================
            # ALPHA-BETA PRUNING
            # =================================================

            if beta <= alpha:

                break

        return min_evaluation


# =========================================================
# FIND BEST AI ACTION
# =========================================================

def get_best_action(
    state,
    depth=3
):

    actions = get_possible_actions(
        state["ai_position"],
        state["player_position"]
    )

    if not actions:

        return "MOVE", 0, 0

    best_action = actions[0]

    best_score = float("-inf")

    nodes = [0]

    alpha = float("-inf")

    beta = float("inf")

    # =====================================================
    # TEST EVERY ACTION
    # =====================================================

    for action in actions:

        new_state = apply_action(
            state,
            action
        )

        score = minimax(
            new_state,
            depth - 1,
            False,
            alpha,
            beta,
            nodes
        )

        if score > best_score:

            best_score = score

            best_action = action

        alpha = max(
            alpha,
            best_score
        )

    return (
        best_action,
        best_score,
        nodes[0]
    )