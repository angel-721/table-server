import gymnasium as gym
import numpy as np
from table_server.envs.table_server_model import TableServerState, AreaIndex, PlayerIndex, ActionIndex, TableServerModel
from gymnasium import spaces

try:
    import pygame
except ImportError as e:
    raise DependencyNotInstalled(
        "{}. (HINT: you can install PyGame dependencies by running 'pip install pygame --user')".format(e))


class TableServerEnv(gym.Env):

    metadata = {'render.modes': ['human', 'rgb_array', 'ansi'],
                "render_fps": 1,
                }

    def __init__(self, render_mode=None, render_fps=None, height=5, width=7, tables=3, meals=3):
        self._render_mode = render_mode
        self._render_fps = render_fps
        self.action_space = spaces.Discrete(6)
        self.height = height
        self.width = width
        self.tables = tables
        self.meals = meals
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
        # self.window_size = (self.cell_size * width, self.cell_size * height)
        return

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = TableServerState(
            self.height, self.width, self.tables, self.meals)
        observation = self.state._restaurant
        info = {}
        return observation, info

    def step(self, action):
        state = self.state
        state_prime = TableServerModel.RESULT(state, action)
        self.state = state_prime

        observation = state_prime._restaurant
        reward = TableServerModel.STEP_COST(state, action, state_prime)
        terminated = TableServerModel.GOAL_TEST(state_prime)
        info = {}
        # display
        return observation, reward, terminated, False, info

        # if self.render_mode is None:
        #     assert self.spec is not None
        #     gym.logger.warn(
        #         "You are calling render method without specifying any render mode. "
        #         "You can specify the render_mode at initialization, "
        #         f'e.g. gym.make("{self.spec.id}", render_mode="rgb_array")'
        #     )
        #     return

        # if self.render_mode == "ansi":
        #     return self._render_text()
        # else:
        #     # return self._render_gui(self.render_mode)
        #     # for now, just return text
        #     return self._render_text()

    def _render_text(self):
        return str(self.state)

    # def _render_gui(self, mode):
    #     if self.window_surface is None:
    #         pygame.init()

    #         if mode == "human":
    #             pygame.display.init()
    #             pygame.display.set_caption("Table Server")
    #             self.window_surface = pygame.display.set_mode(self.window_size)
    #         else:  # rgb_array
    #             self.window_surface = pygame.Surface(self.window_size)
    #     # if self.clock is None:
    #     #     self.clock = pygame.time.Clock()

    #     rect = pygame.Rect((0,0), self.window_size)
    #     pygame.draw.rect(self.window_surface, self.background_color, rect)
    #     for coin in range(self.coin_count):
    #         x = (coin+0.5)*self.cell_size[0]
    #         y = 0.5*self.cell_size[1]
    #         r = 0.4*min(self.cell_size)
    #         if self.state.coin(coin):
    #             color = self.tail_color
    #         else:
    #             color = self.head_color
    #         pygame.draw.circle(self.window_surface, color, (x,y), r)

    #     if mode == "human":
    #         pygame.event.pump()
    #         pygame.display.update()
    #         self.clock.tick(self.metadata["render_fps"])
    #     else:  # rgb_array
    #         return np.transpose(
    #             np.array(pygame.surfarray.pixels3d(self.window_surface)), axes=(1, 0, 2)
    #         )

    # def close(self):
    #     if self.window_surface is not None:
    #         pygame.display.quit()
    #         pygame.quit()
    #     return
