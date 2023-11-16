import gymnasium as gym
import table_server
from table_server.envs import TableServerModel
from gym import envs
from queue import Queue, LifoQueue, PriorityQueue
import numpy as np


class StateNode:
    def __init__(self, state, parent, action, depth, path_cost, heuristic):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.path_cost = path_cost
        self.heuristic = heuristic

    def get_path(self):
        path = np.empty(self.depth, dtype=int)
        node = self
        i = 0
        while node.parent is not None:
            path[i] = node.action
            i += 1
            node = node.parent
        path = np.flip(path)
        return path

    def __lt__(self, other):
        return self.path_cost + self.heuristic < other.path_cost + other.heuristic

    def total_cost(self):
        return self.path_cost + self.heuristic


class Score:
    def __init__(self):
        self.best_score = -1000000
        self.worst_score = 1000000
        self.average_score = 0
        self.total_score = 0
        self.runs = 0
        self.wins = 0

    def update(self, score, win_score=0):
        if score > self.best_score:
            self.best_score = score
        if score < self.worst_score:
            self.worst_score = score
        self.total_score += score
        self.runs += 1
        if score > win_score:
            self.wins += 1

    def get_total(self):
        return self.total_score

    def get_success_rate(self):
        return round(self.wins / self.runs * 100, 2)

    def get_average(self):
        self.average_score = self.total_score / self.runs
        return self.average_score


class Agent:
    def __init__(self, model):
        self.model = model
        self.env = gym.make('table_server/TableServer-v0')
        self.total_score = Score()

    def hash_observation(self, observation):
        return hash(str(observation))

    def a_star_search(self, initial_state, model=TableServerModel):
        print("Initial state:", initial_state)
        reached = {}
        queue = PriorityQueue()

        node = StateNode(initial_state, None, None, 0, 0,
                         model.HEURISTIC(initial_state))
        first_hash = self.hash_observation(initial_state)
        reached[first_hash] = node

        queue.put(node)

        while queue.qsize() > 0:
            # print(queue.qsize(), "Popped a node")
            node = queue.get()

            # print("Goal test")
            if model.GOAL_TEST(node.state):
                return node, True

            for action in model.ACTIONS(node.state):
                # print("Generating a successor")
                # print(action)
                state_prime = model.RESULT(node.state, action)
                hash = self.hash_observation(state_prime)

                if hash not in reached or reached[hash].path_cost > node.path_cost + model.STEP_COST(node.state, action, state_prime):

                    # print("Successor not in reached or has a lower path cost")
                    new_node = StateNode(state_prime, node, action, node.depth + 1,
                                         node.path_cost + model.STEP_COST(node.state, action, state_prime), model.HEURISTIC(state_prime))

                    # print("Adding a node to the queue")
                    queue.put(new_node)
                    reached[hash] = new_node

        return None, False

    def run_agent(self):
        observation, _ = self.env.reset()

        node, solved = self.a_star_search(observation, self.model)
        if not solved or node is None:
            if not solved:
                print("Not solved")
            if node is None:
                print("Node is None")
            print("Failed")
            return 0

        total_reward = 0
        path = node.get_path()
        print("Path:", path)
        print("Path length:", len(path))
        for action in path:
            observation, reward, terminated, truncated, _ = self.env.step(
                action)
            total_reward += reward
        print("Total reward:", total_reward)
        print(self.env.state._restaurant)
        print(observation)
        # print(self.env.state)
        # print(self.env.tables)
        return total_reward


agent = Agent(TableServerModel)
print(agent.run_agent())
