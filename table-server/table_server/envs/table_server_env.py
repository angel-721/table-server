import gymnasium as gym
import numpy as np
from table_server.envs.table_server_model import TableServerState, AreaIndex, PlayerIndex, ActionIndex, TableServerModel
from gymnasium import spaces
import os

try:
    import pygame
except ImportError as e:
    raise DependencyNotInstalled(
        "{}. (HINT: you can install PyGame dependencies by running 'pip install pygame --user')".format(e))

# credit: https://pixelfight.itch.io/birdcat
server_no_food_sheet_path = "../table-server/table_server/envs/imgs/server_0.png"
server_table_1_sheet_path = "../table-server/table_server/envs/imgs/server_1.png"
server_table_2_sheet_path = "../table-server/table_server/envs/imgs/server_2.png"
server_table_3_sheet_path = "../table-server/table_server/envs/imgs/server_3.png"

# all food sprites come from bellow same with the kitchen(fridge)
# credit: https://piiixl.itch.io/mega-pixel-art-32x32-px-icons-sprite-sheet
kitchen_sprite_sheet_path = "../table-server/table_server/envs/imgs/kitchen.png"

# credit: https://havran.itch.io/wooden-barrel
wall_sprite_path = "../table-server/table_server/envs/imgs/barrel.png"

# credit: https://joao9396.itch.io/pixel-nature-pack
table_unserved_sprite_path = "../table-server/table_server/envs/imgs/table.png"
table1_served_path = "../table-server/table_server/envs/imgs/table_1.png"
table2_served_path = "../table-server/table_server/envs/imgs/table_2.png"
table3_served_path = "../table-server/table_server/envs/imgs/table_3.png"

background_sprite_path = "../table-server/table_server/envs/imgs/background.png"


class TableServerEnv(gym.Env):

    metadata = {'render_modes': ['human', 'rgb_array', 'ansi'],
                "render_fps": 20,
                }

    def __init__(self, render_mode=None, height=5, width=7, tables=3, meals=3):
        self.render_mode = render_mode
        self.action_space = spaces.Discrete(6)
        self.height = height
        self.width = width
        self.tables = tables
        self.meals = meals
        self._last_action = None
        self.observation_space = spaces.Dict(
            {
                "area": spaces.Box(low=0, high=6, shape=(height, width), dtype=np.int32),
                "playerStatus": spaces.Discrete(4),
                "kitchen_meals": spaces.Box(low=0, high=3, shape=(3,), dtype=np.int32),
                "table_status": spaces.Box(low=0, high=1, shape=(3,), dtype=np.int32),
            }
        )

        # display stuff
        # self.cell_size = 800 // max(height, width)
        self.cell_size = 64
        self.window_size = (self.cell_size * width, self.cell_size * height)
        self.window_surface = None
        self.clock = None
        return

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = TableServerState(
            self.height, self.width, self.tables, self.meals)
        observation = self.state.observation
        info = {}
        return observation, info

    def step(self, action):
        state = self.state
        state_prime = TableServerModel.RESULT(state, action)
        self.state = state_prime

        observation = state_prime.observation
        reward = TableServerModel.STEP_COST(state, action, state_prime)
        terminated = TableServerModel.GOAL_TEST(state_prime)
        info = {}

        # display
        if self.render_mode == "human":
            self.render(action=action)
        return observation, reward, terminated, False, info

    def render(self, action=None):
        if self.render_mode is None:
            assert self.spec is not None
            gym.logger.warn(
                "Trying to render the environment but render_mode not set. Please set render_mode in the constructor.")
            return

        if self.render_mode == "ansi":
            return self._render_text()
        else:
            return self._render_gui(self.render_mode, action=action)

    def _render_text(self):
        return str(self.state)

    def _render_gui(self, mode, action=None):
        if self.window_surface is None:
            pygame.init()

            if mode == "human":
                pygame.display.init()
                pygame.display.set_caption("Table Server")
                self.window_surface = pygame.display.set_mode(self.window_size)
            else:  # rgb_array
                self.window_surface = pygame.Surface(self.window_size)
        if self.clock is None:
            self.clock = pygame.time.Clock()

        # draw background
        background_sprite = pygame.image.load(background_sprite_path).convert()
        background_sprite = pygame.transform.scale(
            background_sprite, self.window_size)
        background_sprite.set_colorkey((0, 0, 0))
        self.window_surface.blit(background_sprite, (0, 0))

        # draw walls
        walls = np.where(self.state._restaurant["area"] == AreaIndex.WALL)
        for i in range(len(walls[0])):
            # wall_rect = pygame.Rect(
            #     walls[1][i] * self.cell_size, walls[0][i] * self.cell_size, self.cell_size, self.cell_size)
            # pygame.draw.rect(self.window_surface,
            #                  (0, 0, 0), wall_rect)
            wall_sprite = pygame.image.load(
                wall_sprite_path).convert_alpha()
            wall_sprite = pygame.transform.scale(
                wall_sprite, (self.cell_size, self.cell_size))
            self.window_surface.blit(
                wall_sprite, (walls[1][i] * self.cell_size, walls[0][i] * self.cell_size))

        # draw kitchen
        kitchen_col, kitchen_row = np.where(
            self.state._restaurant["area"] == AreaIndex.KITCHEN)
        if len(kitchen_col) >= 1 and len(kitchen_row) >= 1:
            kitchen_sprite = pygame.image.load(
                kitchen_sprite_sheet_path).convert_alpha()
            kitchen_sprite = pygame.transform.scale(
                kitchen_sprite, (self.cell_size, self.cell_size))
            self.window_surface.blit(kitchen_sprite, (kitchen_row[0] * self.cell_size,
                                                      kitchen_col[0] * self.cell_size))

        # draw tables
        table1_col, table1_row = np.where(
            self.state._restaurant["area"] == AreaIndex.TABLE1)
        table2_col, table2_row = np.where(
            self.state._restaurant["area"] == AreaIndex.TABLE2)
        table3_col, table3_row = np.where(
            self.state._restaurant["area"] == AreaIndex.TABLE3)

        # draw table 1
        if len(table1_col) >= 1 and len(table1_row) >= 1:
            if self.state._restaurant["table_status"][0] == 0:
                table_sprite = pygame.image.load(
                    table_unserved_sprite_path).convert_alpha()
            elif self.state._restaurant["table_status"][0] == 1:
                table_sprite = pygame.image.load(
                    table1_served_path).convert_alpha()
            table_sprite = pygame.transform.scale(
                table_sprite, (self.cell_size, self.cell_size))
            self.window_surface.blit(table_sprite, (table1_row[0] * self.cell_size,
                                                    table1_col[0] * self.cell_size))
        # draw table 2
        if len(table2_col) >= 1 and len(table2_row) >= 1:
            if self.state._restaurant["table_status"][1] == 0:
                table_sprite = pygame.image.load(
                    table_unserved_sprite_path).convert_alpha()
            elif self.state._restaurant["table_status"][1] == 1:
                table_sprite = pygame.image.load(
                    table2_served_path).convert_alpha()
            table_sprite = pygame.transform.scale(
                table_sprite, (self.cell_size, self.cell_size))
            self.window_surface.blit(table_sprite, (table2_row[0] * self.cell_size,
                                                    table2_col[0] * self.cell_size))

        # draw table 3
        if len(table3_col) >= 1 and len(table3_row) >= 1:
            if self.state._restaurant["table_status"][2] == 0:
                table_sprite = pygame.image.load(
                    table_unserved_sprite_path).convert_alpha()
            elif self.state._restaurant["table_status"][2] == 1:
                table_sprite = pygame.image.load(
                    table3_served_path).convert_alpha()
            table_sprite = pygame.transform.scale(
                table_sprite, (self.cell_size, self.cell_size))
            self.window_surface.blit(table_sprite, (table3_row[0] * self.cell_size,
                                                    table3_col[0] * self.cell_size))

        player_col, player_row = np.where(
            self.state._restaurant["area"] == AreaIndex.SERVER)

        if self.state._restaurant["playerStatus"] == PlayerIndex.NONE:
            sprite_sheet = pygame.image.load(
                server_no_food_sheet_path).convert_alpha()

        elif self.state._restaurant["playerStatus"] == PlayerIndex.MEAL1:
            sprite_sheet = pygame.image.load(
                server_table_1_sheet_path).convert_alpha()

        elif self.state._restaurant["playerStatus"] == PlayerIndex.MEAL2:
            sprite_sheet = pygame.image.load(
                server_table_2_sheet_path).convert_alpha()
        else:
            sprite_sheet = pygame.image.load(
                server_table_3_sheet_path).convert_alpha()

        if action == ActionIndex.UP:
            frame = 2
        elif action == ActionIndex.DOWN:
            frame = 0
        elif action == ActionIndex.LEFT:
            frame = 3
        elif action == ActionIndex.RIGHT:
            frame = 1
        else:
            if self._last_action == ActionIndex.UP:
                frame = 2
            elif self._last_action == ActionIndex.DOWN:
                frame = 0
            elif self._last_action == ActionIndex.LEFT:
                frame = 3
            elif self._last_action == ActionIndex.RIGHT:
                frame = 1
            else:
                frame = 0
        server = get_image(sprite_sheet, frame, 32, 32, 2, (0, 0, 0))
        self.window_surface.blit(
            server, (player_row[0] * self.cell_size, player_col[0] * self.cell_size))

        if self.render_mode == "human":
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(self.metadata["render_fps"])
            self._last_action = action
        else:  # rgb_array
            return np.transpose(np.array(pygame.surfarray.array3d(self.window_surface)), axes=(1, 0, 2))

    def close(self):
        if self.window_surface is not None:
            pygame.display.quit()
            pygame.quit()
        return


def get_image(sheet, frame, width, height, scale, color):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), ((frame*width), 0, width, height))
    image = pygame.transform.scale(image, (width * scale, height * scale))
    image.set_colorkey(color)
    return image


# env = TableServerEnv(render_mode="human")
# env.reset()
# while True:
#     action = env.action_space.sample()
#     env.step(action)
