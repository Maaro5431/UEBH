import random
import numpy as np
from collections import deque
from keras.api.models import Sequential, load_model
from keras.api.layers import Dense, Activation
from keras.api.optimizers import Adam


class Replay_Buffer(object):
    def __init__(self, input_shape, action_size, memory_size, discrete=False):
        self.memory_size = memory_size  # size of replay memory
        self.mem_cnt = 0
        self.discrete = discrete
        self.state_memory = np.zeros([self.memory_size, input_shape])
        self.new_state_memory = np.zeros([self.memory_size, input_shape])
        dtype = np.int8 if self.discrete else np.float32
        self.action_memory = np.zeros((self.memory_size, action_size), dtype=dtype)
        self.reward_memory = np.zeros(self.memory_size)
        self.terminal_memory = np.zeros(self.memory_size, dtype=np.float32)

    def store_transitions(self, state, action, reward, state_, done):
        index = self.mem_cnt % self.memory_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.terminal_memory[index] = 1 - int(done)
        if self.discrete:
            actions = np.zeros(self.action_memory.shape[1])
            actions[action] = 1.0
            self.action_memory[index] = actions
        else:
            self.action_memory[index] = action
        self.mem_cnt += 1

    def sample_buffer(self, batch_size):
        max_mem = min(self.mem_cnt, self.memory_size)
        batch = np.random.choice(max_mem, batch_size)
        states = self.state_memory[batch]
        states_ = self.new_state_memory[batch]
        rewards = self.reward_memory[batch]
        actions = self.action_memory[batch]
        terminal = self.terminal_memory[batch]

        return states, actions, rewards, states_, terminal


def build_dqn(lr, action_size, input_dims, fc1_dims, fc2_dims):
    model = Sequential(
        [Dense(fc1_dims, input_shape=(input_dims,)), Activation('relu'), Dense(fc2_dims), Activation('relu'),
         Dense(action_size)])
    model.compile(optimizer=Adam(learning_rate=lr), loss="mse")
    return model


class Agent(object):
    def __init__(self, alpha, gamma, action_size, epsilon, batch_size, input_dims, epsilon_dec=0.996, epsilon_end=0.01,
                 mem_size=100000, fname='dqn_model.keras'):  #'dqn_model.keras
        self.q_eval = None
        self.action_space = [i for i in range(action_size)]
        self.action_size = action_size
        self.epsilon = epsilon
        self.gamma = gamma
        self.epsilon_dec = epsilon_dec
        self.epsilon_min = epsilon_end
        self.batch_size = batch_size
        self.model_file = fname

        self.memory = Replay_Buffer(memory_size=mem_size, input_shape=input_dims, action_size=action_size,
                                    discrete=True)
        self.q_eval = build_dqn(alpha, action_size, input_dims, 256, 256)
        # self.load_model()

    def remember(self, state, action, reward, new_state, done):
        self.memory.store_transitions(state, action, reward, new_state, done)

    def choose_action(self, state):
        state1 = np.array(state, dtype=object)
        state1 = np.array([state1]).flatten()
        state = state1[np.newaxis, :]
        rand = np.random.random()
        if rand < self.epsilon:
            action = np.random.choice(self.action_space)
        else:
            state = state[0][-1]  # Extract array([0, 10, 0])
            # Convert to NumPy array with proper dtype and add batch dimension
            state = np.array(state, dtype=np.float32)
            state = np.expand_dims(state, axis=0)  # Shape becomes (1, 3)

            # Make a prediction
            actions = self.q_eval.predict(state)
            action = np.argmax(actions)
        return action

    def learn(self):
        self.q_eval.compile(optimizer='adam', loss='mse')

        if self.memory.mem_cnt < self.batch_size:
            return

        state, action, reward, new_state, done = self.memory.sample_buffer(self.batch_size)
        action_values = np.array(self.action_space, dtype=np.int8)
        action_indices = np.dot(action, action_values)

        q_eval = self.q_eval.predict(state)
        q_next = self.q_eval.predict(new_state)

        q_target = q_eval.copy()

        batch_index = np.arange(self.batch_size, dtype=np.int32)

        q_target[batch_index, action_indices] = reward + self.gamma * np.max(q_next, axis=1) * done
        _ = self.q_eval.fit(state, q_target, verbose=0)
        self.epsilon = self.epsilon * self.epsilon_dec if self.epsilon > self.epsilon_min else self.epsilon_min

    def save_model(self):
        self.q_eval.save(self.model_file)

    def load_model(self):
        self.q_eval = load_model(self.model_file)
