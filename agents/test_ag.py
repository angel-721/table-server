import gymnasium as gym
import table_server
from table_server.envs import TableServerModel
from gym import envs

env = gym.make('table_server/TableServer-v0')
observation, info = env.reset()
print(observation)


# hard code solution
sol = []

# move right 3 times
for i in range(3):
    sol.append(3)

# pick up meal 3
sol.append(4)

# move left 4 times
for i in range(4):
    sol.append(2)

# move up 2 times
for i in range(2):
    sol.append(0)

# move right 4 times
for i in range(4):
    sol.append(3)

# serve meal 3
sol.append(5)


total_reward = 0
for action in sol:
    observation, reward, terminated, _, _ = env.step(action)
    # print(str(observation))
    print(env.state)
    print("ACTIONS: ")
    print(table_server.envs.TableServerModel.ACTIONS(observation))
    # print("reward: " + str(reward))
    total_reward += reward
    if terminated:
        break
print(terminated)
print("total reward: " + str(total_reward))
