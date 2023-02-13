from enum import Enum

import numpy as np
from AstarSearch import *


class Mode(Enum):
    BOUSTROPHEDON = 1,
    A_SEARCH = 2,
    AVOIDING = 3
    STOP = 4
    WAIT = 5
    CONTINUE = 6


up_down_lef_right = {
    "up": lambda x, y: (x, y + 1),
    "down": lambda x, y: (x, y - 1),
    "left": lambda x, y: (x - 1, y),
    "right": lambda x, y: (x + 1, y)
}

calculate_neighbors = {
    "up": lambda x, y: (x, y + 1),
    "down": lambda x, y: (x, y - 1),
    "right": lambda x, y: (x + 1, y),
    "left": lambda x, y: (x - 1, y),
    "ul": lambda x, y: (x - 1, y + 1),
    "dr": lambda x, y: (x + 1, y - 1),
    "ur": lambda x, y: (x + 1, y + 1),
    "dl": lambda x, y: (x - 1, y - 1),
}


class Agent_Vacuum:

    def __init__(self, evn, initial_pos):
        self.actions = evn.actions
        self.state = None
        self.coord = initial_pos
        self.tile_visited = []
        self.obstacles = []
        self.perceive = {}
        self.path_backtracking = []
        self.mode = Mode.BOUSTROPHEDON
        self.send_message = {
            "obstacles": [],
            "tiles": [],
            "backtracking_point": []
        }
        self.last_mode = None
        self.other_agent_pos = []
        self.other_agent_tile_cleaned = []
        self.receive_message = {}
        self.critical_point = []
        self.received_critical_point = []
        self.finished_my_path = False
        self.coordinate_same_area = False
        self.tile_visited.append(self.coord)

    def process_perceive(self):
        for direction in self.perceive:
            x, y = calculate_neighbors[direction](*self.coord)
            if self.perceive[direction] == 2:
                if (x, y) not in self.obstacles:
                    self.obstacles.append((x, y))
                    self.send_message["obstacles"].append((x, y))
            if (x, y) == self.other_agent_pos and self.mode != Mode.CONTINUE:
                self.mode = Mode.AVOIDING
        if not self.mode == Mode.A_SEARCH or not self.coordinate_same_area:
            self.send_message["tiles"].append(self.coord)

    def other_agent_around(self):
        for direction in self.perceive:
            x, y = calculate_neighbors[direction](*self.coord)
            if (x, y) == self.other_agent_pos:
                return True

    def boustrophedon_motion(self):

        direct = ["up", "down", "right", "left"]
        while len(direct) > 0:
            d_ = direct.pop(0)
            x_, y_ = up_down_lef_right[d_](self.coord[0], self.coord[1])
            if self.perceive[d_] not in self.obstacles and (x_, y_) not in self.tile_visited \
                    and (x_, y_) not in self.other_agent_tile_cleaned and (x_, y_) != self.other_agent_pos:
                self.coord = (x_, y_)
                self.visit(x_, y_)
                return d_
            elif d_ == "left":
                self.mode = Mode.A_SEARCH
                return "STAY"

    def backtracking_list(self, tiles):

        eight_direction = {}
        for k in calculate_neighbors:
            group_direction = []
            for points in tiles:
                x, y = calculate_neighbors[k](*points)
                group_direction.append((x, y) not in self.tile_visited and (x, y) not in self.obstacles and (
                    x, y) not in self.other_agent_tile_cleaned)
            eight_direction[k] = np.array(group_direction)

        memory = np.array(tiles)

        cond_a = np.int0(eight_direction["right"] & ~eight_direction["dr"])
        cond_b = np.int0(eight_direction["right"] & ~eight_direction["ur"])
        cond_c = np.int0(eight_direction["left"] & ~eight_direction["dl"])
        cond_d = np.int0(eight_direction["left"] & ~eight_direction["ul"])
        cond_e = np.int0(eight_direction["down"] & ~eight_direction["dl"])
        cond_f = np.int0(eight_direction["down"] & ~eight_direction["dr"])
        sum = (cond_a + cond_b + cond_c + cond_d + cond_e + cond_f)

        backtrack_points = memory[sum > 0]
        if len(backtrack_points) == 0:
            return []
        if self.coordinate_same_area:
            if len(self.received_critical_point) != 0:
                for i, pair in enumerate(backtrack_points):
                    if pair[0] == self.received_critical_point[0] and pair[1] == self.received_critical_point[1]:
                        np.delete(backtrack_points, i)
            if len(backtrack_points) == 0:
                return []
            closest_point_idx = ((backtrack_points - np.array(self.coord)) ** 2).sum(axis=1).argmin()
            self.send_message["backtracking_point"] = backtrack_points[closest_point_idx]
            return tuple(backtrack_points[closest_point_idx])
        closest_point_idx = ((backtrack_points - np.array(self.coord)) ** 2).sum(axis=1).argmin()
        return tuple(backtrack_points[closest_point_idx])

    def select_action(self):
        if self.mode == Mode.BOUSTROPHEDON:
            action = self.boustrophedon_motion()
            if action == "STAY":
                self.critical_point = self.backtracking_list(self.tile_visited)
                if len(self.critical_point) == 0 and not self.coordinate_same_area:
                    self.critical_point = self.backtracking_list(self.other_agent_tile_cleaned)
                    self.finished_my_path = True
                    self.coordinate_same_area = True
                # else:
                #     valid_path = []
                #     for point in self.received_critical_point:
                #         for k in up_down_lef_right:
                #             x, y = up_down_lef_right[k](*point)
                #             if (x, y) not in self.tile_visited:
                #                 valid_path.append(point)
                #                 break
                #     closest_point_idx = ((valid_path - np.array(self.coord)) ** 2).sum(axis=1).argmin()
                #     self.critical_point = tuple(valid_path[closest_point_idx])
                #     self.received_critical_point = []
                if len(self.critical_point) != 0:
                    if self.finished_my_path:
                        map = self.tile_visited.copy()
                        index = len(map)
                        map.extend(self.other_agent_tile_cleaned)
                        self.tile_visited = self.other_agent_tile_cleaned
                        self.other_agent_tile_cleaned = map[:index]
                        self.send_message["cooperation"] = True
                        self.finished_my_path = False
                    else:
                        map = self.tile_visited
                    self.path_backtracking = astar_search(self.coord, tuple(self.critical_point), map, self.other_agent_pos)
                else:
                    self.mode = Mode.STOP
                    return "STAY"
            return action
        elif self.mode == Mode.A_SEARCH:
            action = self.path_backtracking.pop(0)
            x, y = up_down_lef_right[action](*self.coord)
            self.coord = (x, y)
            if len(self.path_backtracking) == 0:
                self.mode = Mode.BOUSTROPHEDON
            return action
        elif self.mode == Mode.WAIT:
            if not self.other_agent_around():
                self.mode = Mode.BOUSTROPHEDON
            return "stay"
        elif self.mode == Mode.CONTINUE:
            self.mode = self.last_mode
            return self.select_action()
        else:
            return "stay"

    def visit(self, x, y):
        self.tile_visited.append((x, y))
        return x, y

    def send(self, agent):
        agent.receive(self.send_message.copy())
        for key in self.send_message:
            self.send_message[key] = []

    def receive(self, message):
        self.receive_message = message
        self.process_message()

    def check_message(self):
        if len(self.send_message["obstacles"]) == 0 and len(self.send_message["tiles"]) == 0:
            return False
        else:
            return True

    def process_message(self):
        if len(self.receive_message["obstacles"]) != 0:
            self.obstacles.extend(self.receive_message["obstacles"])
        if len(self.receive_message["tiles"]) != 0:
            self.other_agent_pos = self.receive_message["tiles"].copy()[0]
            self.other_agent_tile_cleaned.append(self.other_agent_pos)
        if len(self.receive_message["backtracking_point"]) != 0:
            self.received_critical_point = self.receive_message["backtracking_point"].copy()
        if "cooperation" in self.receive_message.keys() and self.coordinate_same_area == False:
            self.coordinate_same_area = self.receive_message["cooperation"]

    def resolve_collide(self, agent):
        agent.last_mode = agent.mode
        agent.mode = Mode.CONTINUE
        self.mode = Mode.WAIT
