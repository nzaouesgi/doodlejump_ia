import random
import time
import arcade
import numpy as np
from sklearn.neural_network import MLPRegressor

X = 0
Y = 1

GAME_WIDTH = 600
GAME_HEIGHT = 30000

VIEWPORT_WIDTH = 800
VIEWPORT_HEIGHT = 1000

PLATFORM_WIDTH = 50

MOVE_X = 10
MOVE_Y = 20

MAX_JUMP_HEIGHT = 250

GRAVITY = 0.60

ACTION_NOTHING = 0
ACTION_GOING_LEFT = 1
ACTION_GOING_RIGHT = 2
ACTIONS = [ ACTION_NOTHING, ACTION_GOING_LEFT, ACTION_GOING_RIGHT ]

LEARNING_RATE = 1
DISCOUNT_FACTOR = 0.1
DECISION_TIMEOUT = 0.15

DEFAULT_REWARD = -1
GOOD_X_REWARD = 1
NEXT_PLATFORM_REWARD = 50
LAST_PLATFORM_REWARD = -5
DEAD_REWARD = -100

def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

class Game(arcade.Window):

    def __init__(self, agent, environment):

        super().__init__(VIEWPORT_WIDTH, VIEWPORT_HEIGHT, "Doodle Jump")

        self.environment = environment
        self.agent = agent

        self.decision_timeout = 0
        self.current_action = ACTION_NOTHING

        self.background = arcade.load_texture("resources/bck.png")

    def setup(self):
        self.environment.reset()
        
        self.last_height = self.environment.current_height

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.environment.player,
                                                             arcade.SpriteList(
                                                                 use_spatial_hash=True),
                                                             GRAVITY)
        self.physics_engine.disable_multi_jump()

        arcade.set_viewport(
                    0,
                    VIEWPORT_WIDTH,
                    0,
                    VIEWPORT_HEIGHT
                )

    def on_draw(self):

        # Clear the screen to the background color
        arcade.start_render()

        (left, _right, bottom, _top) = arcade.get_viewport()

        arcade.draw_lrwh_rectangle_textured(left, bottom,
                                    VIEWPORT_WIDTH, VIEWPORT_HEIGHT,
                                    self.background)

        # Draw our sprites
        self.environment.platforms.draw()
        self.environment.player.draw()

    def set_effective_platforms(self):

        effective_platforms = arcade.SpriteList(use_spatial_hash=True)

        for platform in self.environment.platforms:

            if platform.top <= self.environment.player.bottom:

                effective_platforms.append(platform)

        self.physics_engine.platforms = effective_platforms

    def move_left(self):
        
        self.environment.player.change_x = -MOVE_X
        self.environment.player.set_texture(0)

    def move_right(self):
        
        self.environment.player.change_x = MOVE_X
        self.environment.player.set_texture(1)

    def scroll_viewport(self):

        (_left, _right, bottom, top) = arcade.get_viewport()

        new_bottom = bottom
        new_top = top

        must_scroll = False

        if bottom < self.environment.current_height:
            new_bottom = bottom + 10
            must_scroll = True
        
        if new_top < VIEWPORT_HEIGHT + self.environment.current_height:
            new_top = top + 10
            must_scroll = True

        if must_scroll:
            arcade.set_viewport(
                    0,
                    VIEWPORT_WIDTH,
                    new_bottom,
                    new_top
                )

    def jumped (self):
        self.environment.current_height = self.environment.player.bottom - \
                    self.environment.platforms[0].height
        if self.environment.current_height - 40 > self.last_height:
            # Player landed on the next platform
            self.last_height = self.environment.current_height
            self.agent.learn(self.current_action, self.environment.get_state(), NEXT_PLATFORM_REWARD)
        else:
            # Player landed on last platform
            self.agent.learn(self.current_action, self.environment.get_state(), LAST_PLATFORM_REWARD)
    
    def update_game (self):

        self.set_effective_platforms()

        if self.current_action == ACTION_GOING_LEFT:
            self.move_left()
        elif self.current_action == ACTION_GOING_RIGHT:
            self.move_right()
        else:
            self.environment.player.change_x = 0

        if self.environment.player.change_y <= 0.0:

            if self.physics_engine.can_jump():

                self.jumped()
                self.physics_engine.jump(MOVE_Y)

        self.physics_engine.update()

        if self.environment.player.top <= self.environment.current_height:
            self.setup()
            # Player lost
            self.agent.learn(self.current_action, self.environment.get_state(), DEAD_REWARD)


        if self.environment.player.right < 0:
            self.environment.player.left = VIEWPORT_WIDTH
        elif self.environment.player.left > VIEWPORT_WIDTH:
            self.environment.player.right = 0
        
        self.scroll_viewport()

    def get_horizontal_reward(self):
        reward = DEFAULT_REWARD
        oldEnvironment = self.agent.state
        environment = self.environment.get_state()
        xOldGap = abs(oldEnvironment[1] - oldEnvironment[0])
        xGap = abs(environment[1] - environment[0])
        if xGap < xOldGap:
            reward = GOOD_X_REWARD
        return reward

    def get_reward(self):

        reward = -5

        if self.last_height < self.environment.current_height:
            reward = 100
            self.last_height = self.environment.current_height
        
        elif self.last_height > self.environment.current_height:
            reward = -50
        
        return reward

    def on_update(self, delta_time):

        self.decision_timeout += delta_time

        if self.decision_timeout >= DECISION_TIMEOUT:

            self.current_action = self.agent.best_action()
            self.decision_timeout = 0

            if random.randint(95, 100) > 95:
                self.agent.learn(self.current_action, self.environment.get_state(), self.get_horizontal_reward())

        self.update_game()

class Agent:

    def __init__(self, environment):

        self.environment = environment
        self.policy = Policy()
        self.reset()

    def reset(self):
        self.state = self.environment.get_state()
        self.score = 0

    def best_action (self):
        return self.policy.best_action(self.state)

    def learn(self, action, new_state, reward):
        previous_state = self.state
        self.policy.update(previous_state, new_state, action, reward)
        self.state = new_state
        self.score += reward

class Policy: #ANN
    def __init__(self):
        
        self.learning_rate = LEARNING_RATE
        self.discount_factor = DISCOUNT_FACTOR
        self.actions = ACTIONS
        self.maxX = VIEWPORT_WIDTH + 50
        self.maxY = VIEWPORT_HEIGHT + 50

        self.mlp = MLPRegressor(hidden_layer_sizes = (3,),
                                activation = 'tanh',
                                solver = 'adam',
                                learning_rate_init = self.learning_rate,
                                #max_iter = 1,
                                warm_start = True)
        self.mlp.fit([[0, 0]], [[0, 0, 0]])
        self.q_vector = [ 0, 0, 0 ]

    def __repr__(self):
        return self.q_vector

    def state_to_dataset(self, state):

        return np.array([
            [
                state[0] / self.maxX,
                state[1] / self.maxX
            ]
        ])

    def best_action(self, state):
        dataset = self.state_to_dataset(state)
        self.q_vector = self.mlp.predict(dataset)[0]
        action = self.actions[np.argmax(self.q_vector)]
        return action

    def update(self, previous_state, state, last_action, reward):
        maxQ = np.amax(self.q_vector)
        self.q_vector[last_action] += reward + self.discount_factor * maxQ

        inputs = self.state_to_dataset(previous_state)
        outputs = np.array([self.q_vector])
        self.mlp.fit(inputs, outputs)


class Environment:

    def __init__(self):

        self.level_platforms_coordinates = self.generate_platforms_coordinates()
        self.reset()

    def reset (self):
        self.setup_platforms()
        self.setup_player()
        self.current_height = 0

    def get_next_platform_coordinates(self):
        for i, platform in enumerate(self.platforms):
            if platform.bottom >= self.current_height:
                return self.platforms[i + 1].center_x

    def get_state(self):
        
        return [
            self.player.center_x,
            self.get_next_platform_coordinates()
        ]

    def setup_platforms(self):

        self.platforms = arcade.SpriteList(use_spatial_hash=True)

        for coordinates in self.level_platforms_coordinates:

            sprite = arcade.Sprite("resources/platform.png", 1)

            sprite.center_x = coordinates[X]
            sprite.center_y = coordinates[Y]

            self.platforms.append(sprite)

    def setup_player(self):
        
        first_platform = self.platforms[0]

        filename = "resources/doodle_left.png"

        self.player = arcade.Sprite(scale=0.5)
        for t in load_texture_pair(filename):
            self.player.append_texture(t)
        
        self.player.set_texture(0)
        self.player.center_x = first_platform.center_x
        self.player.bottom = first_platform.bottom + first_platform.height


    def generate_platforms_coordinates(self):

        current_height = 50

        coordinates = [
            ((GAME_WIDTH / 2), current_height)
        ]

        min_decay = 30
        max_decay = 60

        while current_height <= GAME_HEIGHT:

            x = random.randint(
                0,
                GAME_WIDTH - PLATFORM_WIDTH
            )
            y = random.randint(
                #current_height + min_decay,
                current_height + MAX_JUMP_HEIGHT,
                current_height + MAX_JUMP_HEIGHT
                
            )

            if random.choice([ True, False ]):
                if min_decay < max_decay:
                    min_decay += 1

            current_height = y
            c = (x, y)

            coordinates.append(c)

        return coordinates


if __name__ == "__main__":

    environment = Environment()
    agent = Agent(environment)

    window = Game(agent, environment)
    window.setup()
    arcade.run()