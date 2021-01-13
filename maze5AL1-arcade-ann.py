import arcade
import numpy as np
from sklearn.neural_network import MLPRegressor

MAZE = """
##.########
#     #   #
#     #   #
#         #
#         #
########*##
"""

UP, DOWN, LEFT, RIGHT = 'U', 'D', 'L', 'R'
ACTIONS = [UP, DOWN, LEFT, RIGHT]

REWARD_IMPOSSIBLE = -60
REWARD_STUCK = -6
REWARD_DEFAULT = -1
REWARD_GOAL = 60

DEFAULT_LEARNING_RATE = 1
DEFAULT_DISCOUNT_FACTOR = 0.5

SPRITE_SIZE = 64

class Environment:
    def __init__(self, text):
        self.states = {}
        lines = text.strip().split('\n')
        self.height = len(lines)
        self.width = len(lines[0])
        for row in range(self.height):
            for col in range(len(lines[row])):
                self.states[(row, col)] = lines[row][col]
                if lines[row][col] == '.':
                    self.starting_point = (row, col)
                elif lines[row][col] == '*':
                    self.goal = (row, col)

    def apply(self, state, action):
        if action == UP:
            new_state = (state[0] - 1, state[1])
        elif action == DOWN:
            new_state = (state[0] + 1, state[1])
        elif action == LEFT:
            new_state = (state[0], state[1] - 1)
        elif action == RIGHT:
            new_state = (state[0], state[1] + 1)

        if new_state in self.states:
            #calculer la récompense
            if self.states[new_state] in ['#', '.']:
                reward = REWARD_STUCK
            elif self.states[new_state] in ['*']: #Sortie du labyrinthe : grosse récompense
                reward = REWARD_GOAL
            else:
                reward = REWARD_DEFAULT
        else:
            #Etat impossible: grosse pénalité
            new_state = state
            reward = REWARD_IMPOSSIBLE

        return new_state, reward

class Agent:
    def __init__(self, environment):
        self.environment = environment
        self.policy = Policy(ACTIONS, environment.width, environment.height)
        self.reset()        

    def reset(self):
        self.state = environment.starting_point
        self.previous_state = self.state
        self.score = 0

    def best_action(self):
        return self.policy.best_action(self.state)

    def do(self, action):
        self.previous_state = self.state
        self.state, self.reward = self.environment.apply(self.state, action)
        self.score += self.reward
        self.last_action = action

    def update_policy(self):
        self.policy.update(agent.previous_state, agent.state, self.last_action, self.reward)

class Policy: #ANN
    def __init__(self, actions, width, height,
                 learning_rate = DEFAULT_LEARNING_RATE,
                 discount_factor = DEFAULT_DISCOUNT_FACTOR):
        
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.actions = actions
        self.maxX = width
        self.maxY = height

        self.mlp = MLPRegressor(hidden_layer_sizes = (8,),
                                activation = 'tanh',
                                solver = 'sgd',
                                learning_rate_init = self.learning_rate,
                                max_iter = 1,
                                warm_start = True)
        self.mlp.fit([[0, 0]], [[0, 0, 0, 0]])
        self.q_vector = None

    def __repr__(self):
        return self.q_vector

    def state_to_dataset(self, state):
        return np.array([[state[0] / self.maxX, state[1] / self.maxY]])

    def best_action(self, state):
        self.q_vector = self.mlp.predict(self.state_to_dataset(state))[0] #Vérifier que state soit au bon format
        action = self.actions[np.argmax(self.q_vector)]
        return action

    def update(self, previous_state, state, last_action, reward):
        #Q(st, at) = Q(st, at) + learning_rate * (reward + discount_factor * max(Q(state)) - Q(st, at))
        maxQ = np.amax(self.q_vector)
        last_action = ACTIONS.index(last_action)
        print(self.q_vector, maxQ, self.q_vector[last_action])
        self.q_vector[last_action] += reward + self.discount_factor * maxQ

        inputs = self.state_to_dataset(previous_state)
        outputs = np.array([self.q_vector])
        self.mlp.fit(inputs, outputs)

class MazeWindow(arcade.Window):
    def __init__(self, agent):
        super().__init__(agent.environment.width * SPRITE_SIZE,
                         agent.environment.height * SPRITE_SIZE,
                         "Escape from ESGI")
        self.agent = agent

    def setup(self):
        self.walls = arcade.SpriteList()
        
        for state in agent.environment.states:
            if agent.environment.states[state] == '#':
                sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png", 0.5)
                sprite.center_x = sprite.width * (state[1] + 0.5)
                sprite.center_y = sprite.height * (agent.environment.height - state[0] - 0.5)
                self.walls.append(sprite)


        self.goal = arcade.Sprite(":resources:images/items/flagGreen1.png", 0.5)
        self.goal.center_x = self.goal.width * (self.agent.environment.goal[1] + 0.5)
        self.goal.center_y = self.goal.height * (agent.environment.height - self.agent.environment.goal[0] - 0.5)

        self.player = arcade.Sprite(":resources:images/animated_characters/robot/robot_idle.png",
                                    0.5)
        self.update_player_xy()

    def update_player_xy(self):
        self.player.center_x = self.player.height * (self.agent.state[1] + 0.5)
        self.player.center_y = self.player.height * (agent.environment.height - self.agent.state[0] - 0.5)

    def on_update(self, delta_time):
        if agent.state != environment.goal:
            action = self.agent.best_action()
            self.agent.do(action)
            self.agent.update_policy()
            self.update_player_xy()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            self.agent.reset()

    def on_draw(self):
        arcade.start_render()
        
        self.walls.draw()
        self.goal.draw()
        self.player.draw()

        arcade.draw_text(f"Score: {self.agent.score}", 10, 10, arcade.csscolor.WHITE, 20)

if __name__ == "__main__":
    #Initialiser l'environment
    environment = Environment(MAZE)

    #Initialiser l'agent
    agent = Agent(environment)

    #Lancer le jeu
    window = MazeWindow(agent)
    window.setup()
    arcade.run()
