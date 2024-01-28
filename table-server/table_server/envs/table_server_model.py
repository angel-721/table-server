import numpy as np
import copy
import enum
import random


class AreaIndex(enum.IntEnum):
    EMPTY = 0
    TABLE1 = 1
    TABLE2 = 2
    TABLE3 = 3
    KITCHEN = 4
    WALL = 5
    SERVER = 6


class PlayerIndex(enum.IntEnum):
    NONE = 0
    MEAL1 = 1
    MEAL2 = 2
    MEAL3 = 3


class ActionIndex(enum.IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    PICK_UP_MEAL = 4
    SERVE_MEAL = 5


class TableServerState:

    def __init__(self, height=5, width=7, tables=3, meals=3):
        self._height = height
        self._width = width
        self._tables = tables
        self._meals = meals
        self._area = np.zeros((height, width), dtype=np.int32)

        # int to represent what table meal the player is holding
        self._playerStatus = 0

        # 0 = empty, 1 = got meal
        self._table_status = np.zeros((3,), dtype=np.int32)

        self._kitchen_meals = np.array([1, 2, 3], dtype=np.int32)
        self._kitchen_meals = np.random.permutation(self._kitchen_meals)

        self._table_spawns = np.array([[2, 0], [0, 4], [2, 6]])
        self._table_spawns = np.random.permutation(self._table_spawns)
        self._table_1_spawn = self._table_spawns[0]
        self._table_2_spawn = self._table_spawns[1]
        self._table_3_spawn = self._table_spawns[2]

        # spawn walls
        self._area[3][0] = AreaIndex.WALL
        self._area[3][1] = AreaIndex.WALL
        self._area[3][3] = AreaIndex.WALL
        self._area[3][4] = AreaIndex.WALL
        self._area[3][5] = AreaIndex.WALL
        self._area[3][6] = AreaIndex.WALL
        self._area[0][3] = AreaIndex.WALL
        self._area[1][3] = AreaIndex.WALL
        self._area[1][6] = AreaIndex.WALL

        # spawn server
        self._area[4][3] = AreaIndex.SERVER

        # spawn kitchen
        self._area[4][6] = AreaIndex.KITCHEN

        # self._area[table_spawns[0][0]][table_spawns[0][1]] = AreaIndex.TABLE1
        # self._area[table_spawns[1][0]
        #            ][table_spawns[1][1]] = AreaIndex.TABLE2
        # self._area[table_spawns[2][0]
        #            ][table_spawns[2][1]] = AreaIndex.TABLE3

        # randomize table spawns
        self._area[self._table_1_spawn[0]
                   ][self._table_1_spawn[1]] = AreaIndex.TABLE1
        self._area[self._table_2_spawn[0]
                   ][self._table_2_spawn[1]] = AreaIndex.TABLE2
        self._area[self._table_3_spawn[0]
                   ][self._table_3_spawn[1]] = AreaIndex.TABLE3

        # DEBUG

        self._restaurant = {
            "area": self._area,
            "playerStatus": self._playerStatus,
            "kitchen_meals": self._kitchen_meals,
            "table_status": self._table_status,
        }
        return

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def tables(self):
        return self._tables

    @property
    def meals(self):
        return self._meals

    def randomize(self, seed=None):
        if seed is not None:
            np.random.seed(seed)
        self._area = np.random.randint(
            0, AreaIndex.SERVER, size=(self._height, self._width), dtype=np.int32)
        self._playerStatus = 0
        return self

    def turn(self, action):
        """
        UP = 0
        DOWN = 1
        LEFT = 2
        RIGHT = 3
        PICK_UP_MEAL = 4
        SERVE_MEAL = 5
        """
        player_row, player_col = np.where(self._area == AreaIndex.SERVER)
        player_row, player_col = player_row[0], player_col[0]

        # move to area
        if action == ActionIndex.UP:
            if player_row == 0 or self._area[player_row - 1][player_col] == AreaIndex.WALL:
                return
            else:
                self._area[player_row][player_col] = AreaIndex.EMPTY
                self._area[player_row - 1][player_col] = AreaIndex.SERVER
        elif action == ActionIndex.DOWN:
            if player_row == self._height - 1 or self._area[player_row + 1][player_col] == AreaIndex.WALL:
                return
            else:
                self._area[player_row][player_col] = AreaIndex.EMPTY
                self._area[player_row + 1][player_col] = AreaIndex.SERVER
        elif action == ActionIndex.LEFT:
            if player_col == 0 or self._area[player_row][player_col - 1] == AreaIndex.WALL:
                return
            else:
                self._area[player_row][player_col] = AreaIndex.EMPTY
                self._area[player_row][player_col - 1] = AreaIndex.SERVER
        elif action == ActionIndex.RIGHT:
            if player_col == self._width - 1 or self._area[player_row][player_col + 1] == AreaIndex.WALL:
                return
            else:
                self._area[player_row][player_col] = AreaIndex.EMPTY
                self._area[player_row][player_col + 1] = AreaIndex.SERVER

        # pick up meal
        if action == ActionIndex.PICK_UP_MEAL:
            if self._area[player_row][player_col] == self._area[4][6] and self._playerStatus == PlayerIndex.NONE.value and len(self._kitchen_meals) > 0:
                meal = self._kitchen_meals[0]
                self._kitchen_meals = np.delete(self._kitchen_meals, 0)
                self._playerStatus = meal

        # serve meal
        if action == ActionIndex.SERVE_MEAL:
            if self._area[self._table_1_spawn[0]][self._table_1_spawn[1]] == AreaIndex.SERVER and self._playerStatus == PlayerIndex.MEAL1.value:
                self._table_status[0] = 1
                self._playerStatus = PlayerIndex.NONE.value

            elif self._area[self._table_2_spawn[0]][self._table_2_spawn[1]] == AreaIndex.SERVER and self._playerStatus == PlayerIndex.MEAL2.value:
                self._table_status[1] = 1
                self._playerStatus = PlayerIndex.NONE.value

            elif self._area[self._table_3_spawn[0]][self._table_3_spawn[1]] == AreaIndex.SERVER and self._playerStatus == PlayerIndex.MEAL3.value:
                self._table_status[2] = 1
                self._playerStatus = PlayerIndex.NONE.value

            else:
                return

        # reset table and kitchen after moves after player moves off of them
        if not self._area[4][6] == AreaIndex.SERVER:
            self._area[4][6] = AreaIndex.KITCHEN

        if self._area[self._table_1_spawn[0]][self._table_1_spawn[1]] != AreaIndex.SERVER:
            self._area[self._table_1_spawn[0]
                       ][self._table_1_spawn[1]] = AreaIndex.TABLE1
        if self._area[self._table_2_spawn[0]][self._table_2_spawn[1]] != AreaIndex.SERVER:
            self._area[self._table_2_spawn[0]
                       ][self._table_2_spawn[1]] = AreaIndex.TABLE2
        if self._area[self._table_3_spawn[0]][self._table_3_spawn[1]] != AreaIndex.SERVER:
            self._area[self._table_3_spawn[0]
                       ][self._table_3_spawn[1]] = AreaIndex.TABLE3

        # set new restaurant state
        self._restaurant = {
            "area": self._area,
            "playerStatus": self._playerStatus,
            "kitchen_meals": self._kitchen_meals,
            "table_status": self._table_status,
        }

    @property
    def observation(self):
        return self._restaurant

    @observation.setter
    def observation(self, value):
        self._restaurant = value
        self._area = value["area"]
        self._height = value["area"].shape[0]
        self._width = value["area"].shape[1]
        self._tables = 3
        self._meals = 3
        return

    def __str__(self):
        s = ""
        grid = ""
        for row in range(0, self.height):
            for col in range(0, self.width):
                if self._area[row][col] == AreaIndex.EMPTY:
                    grid += ". "
                elif self._area[row][col] == AreaIndex.TABLE1:
                    grid += "1 "
                elif self._area[row][col] == AreaIndex.TABLE2:
                    grid += "2 "
                elif self._area[row][col] == AreaIndex.TABLE3:
                    grid += "3 "
                elif self._area[row][col] == AreaIndex.KITCHEN:
                    grid += "K "
                elif self._area[row][col] == AreaIndex.WALL:
                    grid += "W "
                elif self._area[row][col] == AreaIndex.SERVER:
                    grid += "S "
            grid += "\n"

        s += "Area:\n"
        s += grid + "\n"
        s += "Player Status: " + str(self._playerStatus) + "\n"
        s += "Kitchen Meals: " + str(self._kitchen_meals) + "\n"
        s += "Table Status: " + str(self._table_status) + "\n"
        return s


class TableServerModel:

    def ACTIONS(state):
        statePointer = None
        if type(state) != dict:
            statePointer = state.observation
        else:
            statePointer = state
        actions = [ActionIndex.UP.value, ActionIndex.DOWN.value,
                   ActionIndex.LEFT.value, ActionIndex.RIGHT.value,
                   ActionIndex.PICK_UP_MEAL.value, ActionIndex.SERVE_MEAL.value]

        # find player
        player_row, player_col = np.where(
            statePointer["area"] == AreaIndex.SERVER.value)

        # can't serve meal if player is not holding a meal
        if statePointer["playerStatus"] == PlayerIndex.NONE.value:
            actions.remove(ActionIndex.SERVE_MEAL.value)

        # can't pick up meal if player is already holding a meal
        if statePointer["playerStatus"] != PlayerIndex.NONE.value or statePointer["area"][4][6] != AreaIndex.SERVER.value:
            actions.remove(ActionIndex.PICK_UP_MEAL.value)

        # can't move up if player is at the top of the map or if there is a wall above
        if player_row == 0:
            actions.remove(ActionIndex.UP.value)
        else:
            if statePointer["area"][player_row - 1][0][player_col] == AreaIndex.WALL.value:
                actions.remove(ActionIndex.UP.value)

        if player_col == 0 or statePointer["area"][player_row][0][player_col - 1] == AreaIndex.WALL.value:
            actions.remove(ActionIndex.LEFT.value)

        if player_row == statePointer["area"].shape[0] - 1 or statePointer["area"][player_row + 1][0][player_col] == AreaIndex.WALL.value:
            actions.remove(ActionIndex.DOWN.value)

        if player_col == statePointer["area"].shape[1] - 1 or statePointer["area"][player_row][0][player_col + 1] == AreaIndex.WALL.value:
            actions.remove(ActionIndex.RIGHT.value)

        return actions

    def RESULT(state, action):
        statePointer = None

        if type(state) == dict:
            statePointer = TableServerState()
            statePointer._restaurant = state
            statePointer._area = state["area"]
            statePointer._playerStatus = state["playerStatus"]
            statePointer._kitchen_meals = state["kitchen_meals"]
            statePointer._table_status = state["table_status"]
            statePointer.observation = state
            statePointer._height = state["area"].shape[0]
            statePointer._width = state["area"].shape[1]

            table_1_spawn = np.where(
                statePointer._area == AreaIndex.TABLE1.value)
            table_2_spawn = np.where(
                statePointer._area == AreaIndex.TABLE2.value)
            table_3_spawn = np.where(
                statePointer._area == AreaIndex.TABLE3.value)

            statePointer._table_1_spawn = np.array(
                [table_1_spawn[0][0], table_1_spawn[1][0]])
            statePointer._table_2_spawn = np.array(
                [table_2_spawn[0][0], table_2_spawn[1][0]])
            statePointer._table_3_spawn = np.array(
                [table_3_spawn[0][0], table_3_spawn[1][0]])
        else:
            statePointer = state

        state_prime = copy.deepcopy(statePointer)
        state_prime.turn(action)
        return state_prime

    def GOAL_TEST(state):
        goal_test = True

        if type(state) != dict:
            statePointer = state.observation
        else:
            statePointer = state

        if statePointer["table_status"][0] == 0:
            goal_test = False
        if statePointer["table_status"][1] == 0:
            goal_test = False
        if statePointer["table_status"][2] == 0:
            goal_test = False
        if statePointer["kitchen_meals"].size > 0:
            goal_test = False
        if statePointer["playerStatus"] != PlayerIndex.NONE.value:
            goal_test = False

        # if goal_test:
            # print("FOUND THE GOAL!")
            # print(statePointer)

        return goal_test

    def FIRST_GOAL_TEST(state):
        goal_test = True

        if type(state) != dict:
            statePointer = state.observation
        else:
            statePointer = state

        if statePointer["kitchen_meals"].size > 2:
            goal_test = False

        # if goal_test:
            # print("FOUND THE GOAL!")
            # print(statePointer)

        return goal_test

    def SECOND_GOAL_TEST(state):
        goal_test = True

        if type(state) != dict:
            statePointer = state.observation
        else:
            statePointer = state

        if np.array_equal(statePointer["table_status"], np.array([0, 0, 0])):
            goal_test = False

        # if goal_test:
            # print("FOUND THE GOAL!")
            # print(statePointer)
        return goal_test

    def THIRD_GOAL_TEST(state):
        goal_test = True

        if type(state) != dict:
            statePointer = state.observation
        else:
            statePointer = state

        if statePointer["playerStatus"] != PlayerIndex.NONE.value:
            goal_test = False

        # if goal_test:
            # print("FOUND THE GOAL!")
            # print(statePointer)
        return goal_test

    """
    A*,UCS,Greedy always assume that step cost is positive
    reward system is set up so the lower the cost, the better
    """
    def STEP_COST(state, action, state_prime):
        if action == ActionIndex.PICK_UP_MEAL.value and state._restaurant["playerStatus"] == PlayerIndex.NONE.value:
            return 1

        elif action == ActionIndex.PICK_UP_MEAL.value and state._restaurant["playerStatus"] != PlayerIndex.NONE.value:
            return 1

        elif action == ActionIndex.UP.value or action == ActionIndex.DOWN.value or action == ActionIndex.LEFT.value or action == ActionIndex.RIGHT.value:
            return 1

        elif action == ActionIndex.SERVE_MEAL.value and state._restaurant["playerStatus"] == PlayerIndex.NONE.value:
            return 1

        elif action == ActionIndex.SERVE_MEAL.value and state._restaurant["playerStatus"] != PlayerIndex.NONE.value:
            if state._restaurant["table_status"][0] == 0 and state_prime._restaurant["table_status"][0] == 1 and state._restaurant["playerStatus"] == PlayerIndex.MEAL1.value:
                return 0
            elif state._restaurant["table_status"][1] == 0 and state_prime._restaurant["table_status"][1] == 1 and state._restaurant["playerStatus"] == PlayerIndex.MEAL2.value:
                return 0
            elif state._restaurant["table_status"][2] == 0 and state_prime._restaurant["table_status"][2] == 1 and state._restaurant["playerStatus"] == PlayerIndex.MEAL3.value:
                return 0
            else:
                return 1

        elif TableServerModel.GOAL_TEST(state_prime):
            return 0

    # def HEURISTIC(state):
    #     return 0

    def HEURISTIC(state):
        if type(state) != dict:
            statePointer = state.observation
        else:
            statePointer = state
        player_row, player_col = np.where(
            statePointer["area"] == AreaIndex.SERVER)
        kitchen_row, kitchen_col = np.where(
            statePointer["area"] == AreaIndex.KITCHEN)
        table_1_row, table_1_col = np.where(
            statePointer["area"] == AreaIndex.TABLE1)
        table_2_row, table_2_col = np.where(
            statePointer["area"] == AreaIndex.TABLE2)
        table_3_row, table_3_col = np.where(
            statePointer["area"] == AreaIndex.TABLE3)
        manhattan_distance = 0

        if kitchen_col.size == 0 or table_1_col.size == 0 or table_2_col.size == 0 or table_3_col.size == 0:
            return 0

        if statePointer["playerStatus"] == PlayerIndex.NONE.value:
            manhattan_distance = abs(
                player_row[0] - kitchen_row[0]) + abs(player_col[0] - kitchen_col[0])
        elif statePointer["playerStatus"] == PlayerIndex.MEAL1.value:
            manhattan_distance = abs(
                player_row[0] - table_1_row[0]) + abs(player_col[0] - table_1_col[0])
        elif statePointer["playerStatus"] == PlayerIndex.MEAL2.value:
            manhattan_distance = abs(
                player_row[0] - table_2_row[0]) + abs(player_col[0] - table_2_col[0])
        elif statePointer["playerStatus"] == PlayerIndex.MEAL3.value:
            manhattan_distance = abs(
                player_row[0] - table_3_row[0]) + abs(player_col[0] - table_3_col[0])
        return manhattan_distance


if __name__ == "__main__":
    thingy = TableServerState()
    # print(thingy)
