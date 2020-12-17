import pygame
import math
from queue import PriorityQueue

WIDTH = 500
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Search")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


# spot
class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def get_position(self):
        return self.row, self.col

    def is_visited(self):
        return self.color == GREEN

    def is_open(self):
        return self.color == GREEN

    def is_blocked(self):
        return self.color == BLACK

    def is_start_node(self):
        return self.color == ORANGE

    def is_goal_node(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_visited(self):
        self.color = YELLOW

    def make_open(self):
        self.color = GREEN

    def make_blocked(self):
        self.color = BLACK

    def make_goal_node(self):
        self.color = TURQUOISE

    def make_start_node(self):
        self.color = ORANGE

    def make_path(self):
        self.color = RED

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        self.neighbours = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_blocked():  # Search downwards
            self.neighbours.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_blocked():  # Search upwards
            self.neighbours.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_blocked():  # Search right
            self.neighbours.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_blocked():  # Search left
            self.neighbours.append(grid[self.row][self.col - 1])

    # lt stands for less than
    def __lt__(self, other):
        return False


# the heuristic is calculated using the Manhattan distance measure
def heuristic_manhattan(p1, p2):
    x1,y1 = p1
    x2,y2 = p2
    return abs(x2-x1) + abs(y2-y1)

# using euclidean distance as the heuristic
def heuristic_euclidean(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((y2-x2)**2 + (y1-x1)**2)


def highlight_path(last_node, current, draw):
    while current in last_node:
        current = last_node[current]
        current.make_path()
        draw()


def search(draw, grid, start_node, goal_node, euclidean):
    euclidean = False
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start_node))
    last_node = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start_node] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start_node] = heuristic_manhattan(start_node.get_position(), goal_node.get_position())

    open_set_hash = {start_node}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == goal_node:
            highlight_path(last_node, goal_node, draw)
            goal_node.make_goal_node()
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbour] and euclidean == False:
                last_node[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + heuristic_euclidean(neighbour.get_position(), goal_node.get_position())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()
            elif temp_g_score < g_score[neighbour] and euclidean == True:
                last_node[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + heuristic_manhattan(neighbour.get_position(), goal_node.get_position())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()


        draw()

        if current != start_node:
            current.make_visited()

    return False


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid


def draw_grid(window, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(window, GREY, (0, i * gap), (width, i * gap))
    for j in range(rows):
        pygame.draw.line(window, GREY, (j * gap, 0), (j * gap, width))


def draw(window, grid, rows, width):
    window.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(window)

    draw_grid(window, rows, width)
    pygame.display.update()


def get_clicked_position(mouse_position, rows, width):
    gap = width // rows
    y, x = mouse_position
    row = y // gap
    col = x // gap

    return row, col


def main(window, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start_node = None
    goal_node = None

    run = True
    started = False

    while run:
        draw(window, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                position = pygame.mouse.get_pos()
                row, col = get_clicked_position(position, ROWS, width)
                node = grid[row][col]
                if not start_node and node != goal_node:
                    start_node = node
                    start_node.make_start_node()

                elif not goal_node and node != start_node:
                    goal_node = node
                    goal_node.make_goal_node()

                elif node != goal_node and node != start_node:
                    node.make_blocked()

            elif pygame.mouse.get_pressed()[2]:
                position = pygame.mouse.get_pos()
                row, col = get_clicked_position(position, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start_node:
                    start_node = None
                elif node == goal_node:
                    goal_node = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                    search(lambda: draw(window, grid, ROWS, width), grid, start_node, goal_node, True)
                elif event.key == pygame.K_RSHIFT and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                    search(lambda: draw(window, grid, ROWS, width), grid, start_node, goal_node, False)

    pygame.quit()


main(WINDOW, WIDTH)
