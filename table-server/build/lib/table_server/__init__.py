from gymnasium.envs.registration import register

from table_server.envs.table_server_env import TableServerEnv
from table_server.envs.table_server_model import TableServerModel
from table_server.envs.table_server_model import TableServerState

register(
    id="table_server/TableServer-v0",

    entry_point="table_server.envs:TableServerEnv",

    max_episode_steps=80,
)
