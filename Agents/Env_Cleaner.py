import numpy as np
import cv2


class Env:
    actions = ["up", "down", "left", "right"]
    states = ["MOVING", "DO_NOTHING"]

    def __init__(self, x_dim=20, y_dim=20, obstacle_num=10, agent_position=[]):
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.obstacle_pos = []
        self.agent = agent_position
        self.dx = 0
        self.dy = 0
        self.direction = "SOUTH"
        self.obstacle_num = obstacle_num
        self.room_map = np.zeros((self.x_dim, self.y_dim))
        self.get_init_state()
        self.cleaner_state = None

    def step(self, action=None):
        if action is None:
            action = ["stay", "stay"]
        perception = []
        for i in range(len(self.agent)):
            reward = 0
            if action[i] == "up":
                if self.agent[i][0] > 0 and self.room_map[self.agent[i][0] - 1][self.agent[i][1]] != 2:
                    self.agent[i][0] -= 1
                    self.cleaner_state = "MOVING"
                else:
                    self.cleaner_state = "DO_NOTHING"
            elif action[i] == "down":
                if self.agent[i][0] < self.x_dim - 1 and self.room_map[self.agent[i][0] + 1][self.agent[i][1]] != 2:
                    self.agent[i][0] += 1
                    self.cleaner_state = "MOVING"
                else:
                    self.cleaner_state = "DO_NOTHING"
            elif action[i] == "left":
                if self.agent[i][1] > 0 and self.room_map[self.agent[i][0]][self.agent[i][1] - 1] != 2:
                    self.agent[i][1] -= 1
                    self.cleaner_state = "MOVING"
                else:
                    self.cleaner_state = "DO_NOTHING"
            elif action[i] == "right":
                if self.agent[i][1] < self.y_dim - 1 and self.room_map[self.agent[i][0]][self.agent[i][1] + 1] != 2:
                    self.agent[i][1] += 1
                    self.cleaner_state = "MOVING"
                else:
                    self.cleaner_state = "DO_NOTHING"
            if self.room_map[self.agent[i][0]][self.agent[i][1]] == 0:
                self.room_map[self.agent[i][0]][self.agent[i][1]] = 1
                reward += 1

            sensor_result = {
                "up": self.room_map[self.agent[i][0] - 1][self.agent[i][1]],
                "down": self.room_map[self.agent[i][0] + 1][self.agent[i][1]],
                "right": self.room_map[self.agent[i][0]][self.agent[i][1] + 1],
                "left": self.room_map[self.agent[i][0]][self.agent[i][1] - 1],
                "ul": self.room_map[self.agent[i][0] - 1][self.agent[i][1] - 1],
                "dr": self.room_map[self.agent[i][0] + 1][self.agent[i][1] + 1],
                "ur": self.room_map[self.agent[i][0] - 1][self.agent[i][1] + 1],
                "dl": self.room_map[self.agent[i][0] + 1][self.agent[i][1] - 1],
            }
            perception.append(sensor_result)

        return perception

    def get_init_state(self):
        self.room_map = []
        self.room_map = np.load('map.npy')
        self.x_dim = len(self.room_map[0])
        self.y_dim = len(self.room_map)
        for i in range(len(self.agent)):
            self.room_map[self.agent[i][0]][self.agent[i][1]] = 1

    def render(self):

        rectangle_size = 20
        self.room = np.ones((self.x_dim * rectangle_size, self.y_dim * rectangle_size, 3))

        for i in range(self.x_dim):
            for j in range(self.y_dim):
                if self.room_map[i][j] == 2:
                    cv2.rectangle(self.room, (i * rectangle_size, j * rectangle_size),
                                  (i * rectangle_size + rectangle_size, j * rectangle_size + rectangle_size),
                                  (0, 0, 0), -1)
                if self.room_map[i][j] == 0:
                    cv2.rectangle(self.room, (i * rectangle_size, j * rectangle_size),
                                  (i * rectangle_size + rectangle_size, j * rectangle_size + rectangle_size),
                                  (255, 0, 0), -1)
                if (i == self.agent[0][0] and j == self.agent[0][1]) or (
                        i == self.agent[1][0] and j == self.agent[1][1]):
                    cv2.rectangle(self.room, (i * rectangle_size, j * rectangle_size),
                                  (i * rectangle_size + rectangle_size, j * rectangle_size + rectangle_size),
                                  (0, 255, 0), -1)

        cv2.imshow("Cleaner Agent", self.room)
        cv2.waitKey(1)
