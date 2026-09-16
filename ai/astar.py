import heapq


# =========================================================
# MANHATTAN DISTANCE
# =========================================================

def heuristic(current, goal):

    current_row, current_col = current
    goal_row, goal_col = goal

    return (
        abs(current_row - goal_row)
        +
        abs(current_col - goal_col)
    )


# =========================================================
# GET VALID NEIGHBORS
# =========================================================

def get_neighbors(
    position,
    rows,
    cols,
    obstacles
):

    row, col = position

    directions = [
        (-1, 0),  # UP
        (1, 0),   # DOWN
        (0, -1),  # LEFT
        (0, 1),   # RIGHT
    ]

    neighbors = []

    for row_change, col_change in directions:

        new_row = row + row_change
        new_col = col + col_change

        # Check grid boundary

        if new_row < 0 or new_row >= rows:
            continue

        if new_col < 0 or new_col >= cols:
            continue

        new_position = (
            new_row,
            new_col
        )

        # Check obstacle

        if new_position in obstacles:
            continue

        neighbors.append(
            new_position
        )

    return neighbors


# =========================================================
# RECONSTRUCT PATH
# =========================================================

def reconstruct_path(
    came_from,
    current
):

    path = [current]

    while current in came_from:

        current = came_from[current]

        path.append(current)

    path.reverse()

    return path


# =========================================================
# A* SEARCH
# =========================================================

def a_star(
    start,
    goal,
    rows,
    cols,
    obstacles
):

    # Priority queue
    #
    # (f_score, position)

    open_set = []

    heapq.heappush(
        open_set,
        (
            0,
            start
        )
    )

    # Parent of every node

    came_from = {}

    # Cost from start

    g_score = {
        start: 0
    }

    # Estimated total cost

    f_score = {
        start: heuristic(
            start,
            goal
        )
    }

    nodes_explored = 0

    while open_set:

        # Get lowest f-score node

        current_f, current = heapq.heappop(
            open_set
        )

        nodes_explored += 1

        # Goal reached

        if current == goal:

            path = reconstruct_path(
                came_from,
                current
            )

            return path, nodes_explored

        # Check neighbors

        neighbors = get_neighbors(
            current,
            rows,
            cols,
            obstacles
        )

        for neighbor in neighbors:

            # Every movement costs 1

            tentative_g = (
                g_score[current]
                + 1
            )

            # If this is a better path

            if (
                neighbor not in g_score
                or tentative_g < g_score[neighbor]
            ):

                came_from[neighbor] = current

                g_score[neighbor] = tentative_g

                f_score[neighbor] = (
                    tentative_g
                    +
                    heuristic(
                        neighbor,
                        goal
                    )
                )

                heapq.heappush(
                    open_set,
                    (
                        f_score[neighbor],
                        neighbor
                    )
                )

    # No path found

    return [], nodes_explored