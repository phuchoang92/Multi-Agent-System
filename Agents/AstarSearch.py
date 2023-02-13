up_down_lef_right = {
    "up": lambda x, y: (x, y + 1),
    "down": lambda x, y: (x, y - 1),
    "left": lambda x, y: (x - 1, y),
    "right": lambda x, y: (x + 1, y)
}


def heuristic(start, goal):
    D = 1
    D2 = 1
    dx = abs(start[0] - goal[0])
    dy = abs(start[1] - goal[1])
    return D * (dx + dy)


def get_vertex_neighbours(pos, graph, exception_point):
    n = []
    for direc in {"right", "left", "up", "down"}:
        x2, y2 = up_down_lef_right[direc](*pos)
        if (x2, y2) not in graph or (x2, y2) == exception_point:
            continue
        n.append(((x2, y2), direc))
    return n


def astar_search(start, end, graph, exception_point):
    G = {}  # Actual movement cost to each position from the start position
    F = {}  # Estimated movement cost of start to end going via this position

    G[start] = 0
    F[start] = heuristic(start, end)

    closedVertices = set()
    openVertices = {start}
    cameFrom = {}

    while len(openVertices) > 0:

        current = None
        currentFscore = None
        for pos in openVertices:
            if current is None or F[pos] < currentFscore:
                currentFscore = F[pos]
                current = pos

        # Check if we have reached the goal
        if current == end:
            path = []
            while current in cameFrom:
                current, action = cameFrom[current]
                path.append(action)
            path.reverse()
            return path

        # Mark the current vertex as closed
        openVertices.remove(current)
        closedVertices.add(current)

        # Update scores for vertices near the current position
        for neighbour, direc in get_vertex_neighbours(current, graph, exception_point):
            if neighbour in closedVertices:
                continue  # We have already processed this node exhaustively
            candidateG = G[current] + 1

            if neighbour not in openVertices:
                openVertices.add(neighbour)  # Discovered a new vertex

            elif candidateG >= G[neighbour]:
                continue  # This G score is worse than previously found

            # Adopt this G score
            cameFrom[neighbour] = (current, direc)
            G[neighbour] = candidateG
            H = heuristic(neighbour, end)
            F[neighbour] = G[neighbour] + H

    raise RuntimeError("A* failed to find a solution")


def astar_path(Memory, path):
    for q in path:
        x = q[0]
        y = q[1]
        Memory.append((x, y))
