import gymnasium as gym
import table_server
from table_server.envs import TableServerModel
from gym import envs
from queue import Queue, LifoQueue, PriorityQueue
import numpy as np
from time import time
from enum import IntEnum


class Search(IntEnum):
    A_STAR = 0
    GREEDY_BEST_FIRST_SEARCH = 1
    UNIFORM_COST_SEARCH = 2


class Goal(IntEnum):
    FIRST = 0
    SECOND = 1
    THIRD = 2


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
        self.best_score = float('-inf')
        self.worst_score = float('inf')
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

    def reset(self):
        self.best_score = float('-inf')
        self.worst_score = float('inf')
        self.average_score = 0
        self.total_score = 0
        self.runs = 0
        self.wins = 0


class Agent:
    def __init__(self, model, use_gui=False):
        self.model = model
        # self.env = gym.make('table_server/TableServer-v0', render_mode="human")
        if use_gui:
            self.env = gym.make(
                'table_server/TableServer-v0', render_mode="human")
        else:
            self.env = gym.make(
                'table_server/TableServer-v0', render_mode=None)
        self.total_score = Score()
        self.SEARCHES = [self.a_star_search,
                         self.greedy_best_first_search, self.uniform_cost_search]
        self.GOALS = [self.model.FIRST_GOAL_TEST,
                      self.model.SECOND_GOAL_TEST, self.model.GOAL_TEST]

    def hash_observation(self, observation):
        return hash(str(observation))

    def a_star_search(self, initial_state, model=TableServerModel):
        # print("Initial state:", initial_state)
        reached = {}
        queue = PriorityQueue()

        node = StateNode(initial_state, None, None, 0, 0,
                         model.HEURISTIC(initial_state))
        first_hash = self.hash_observation(initial_state)
        reached[first_hash] = node

        queue.put(node)

        while queue.qsize() > 0:
            # print(queue.qsize(), "Popped a node")
            # print(queue.qsize())
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
                    # print("Reached:", len(reached))
                    reached[hash] = new_node

        return None, False

    def greedy_best_first_search(self, initial_state, model=TableServerModel):
        # print("Greedy best first search")
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

                if hash not in reached or reached[hash].heuristic > model.HEURISTIC(state_prime):

                    # print("Successor not in reached or has a lower path cost")
                    new_node = StateNode(state_prime, node, action, node.depth + 1,
                                         node.path_cost + model.STEP_COST(node.state, action, state_prime), model.HEURISTIC(state_prime))

                    # print("Adding a node to the queue")
                    queue.put(new_node)
                    reached[hash] = new_node

        return None, False

    def uniform_cost_search(self, initial_state, model=TableServerModel):
        # print("Uniform cost search")
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

    def run_agent(self, search=Search.A_STAR, run_many_times=False):
        startTime = time()
        observation, _ = self.env.reset()
        self.env.render()
        # print(observation)

        search = self.SEARCHES[search]

        node, solved = search(observation, self.model)

        if not solved and node is None:
            if not solved:
                print("Not solved")
            if node is None:
                print("Node is None")
            print("Failed")
            return 0

        path = node.get_path()
        total_reward = 0

        for action in path:
            observation, reward, terminated, truncated, _ = self.env.step(
                action)
            total_reward += reward
            self.env.render()

        if not run_many_times:
            print("Total reward:", total_reward)
        # print(observation)

        total_time = time() - startTime
        self.total_score.update(total_reward, 0)
        return total_reward, total_time

    def run_many_times(self, times, search=Search.A_STAR):
        total_score = 0
        total_time = 0
        attempts = 0
        for i in range(times):
            score, time = self.run_agent(search, True)
            total_score += score
            total_time += time
            attempts += 1
            if i == 100:
                print("100 runs")
            if i == 500:
                print("500 runs")
            if i == 1000:
                print("1000 runs")
            if i == 2500:
                print("2500 runs")
            if i == 5000:
                print("5000 runs")
        print("SEARCH:", search)
        print("Highest score:", self.total_score.best_score)
        print("Lowest score:", self.total_score.worst_score)
        print("Average score:", round(self.total_score.get_average(), 2))
        print("Average time:", str(round(total_time / times, 2)) + " s")
        self.total_score.reset()
        total_score = 0
        total_time = 0
        attempts = 0

    def run_all_searches(self, times):
        for search in Search:
            self.run_many_times(times, search)


run_times = 5000
agent = Agent(TableServerModel, True)
# agent.run_all_searches(run_times)
agent.run_agent(Search.A_STAR)
