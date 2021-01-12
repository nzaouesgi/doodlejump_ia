import numpy as np
from sklearn.neural_network import MLPRegressor


DEFAULT_LEARNING_RATE = 1
DEFAULT_DISCOUNT_FACTOR = 0.5

class Policy:

    def __init__(self, actions, width, height,
                 learning_rate = DEFAULT_LEARNING_RATE,
                 discount_factor = DEFAULT_DISCOUNT_FACTOR):

        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.actions = actions
        self.maxX = width
        self.maxY = height

        # Configuration du modèle
        self.mlp = MLPRegressor(hidden_layer_sizes = (2,),
                                activation = 'tanh',
                                solver = 'sgd',
                                learning_rate_init = self.learning_rate,
                                max_iter = 1,
                                warm_start = False)

        # Initialisation modèle
        self.mlp.fit([0,0],[0,0])
        self.q_vector = None

    def __repr__(self):
        return self.q_vector

    def state_to_dataset(self, state):
        # Create data set from current state
        return np.array()

    def best_action(self, state):
        self.q_vector = self.mlp.predict(self.state_to_dataset(state))[0]
        action = self.actions[np.argmax(self.q_vector)]
        return action

    def update(self, previous_state, state, last_action, reward):
        maxQ = np.amax(self.q_vector)
        # Update last_action
        last_action = self.actions.index(last_action)
        self.q_vector[last_action] += reward + self.discount_factor * maxQ

        inputs = self.state_to_dataset(previous_state)
        outputs = np.array([self.q_vector])
        self.mlp.fit(inputs, outputs)
