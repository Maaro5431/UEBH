import time

import numpy as np
from Game_env import UEBH_env
from keras._tf_keras import keras
from DQN import Agent

from numpy import loadtxt
from keras.api.saving import load_model
from keras.api.models import Sequential
from keras.api.layers import Dense, Activation

# load and evaluate a saved model
from numpy import loadtxt

# load model
model = load_model('dqn_model2.keras', custom_objects=None, compile=True, safe_mode=True)

# summarize model.
model.summary()
env = UEBH_env()

done = False
num_games = 5
for i in range(num_games):
    score = 0
    state = env.reset()
    done = False
    observation = np.expand_dims(np.array(state.observation, dtype=np.float32), axis=0)
    while not done:
        actions = model.predict(observation)
        action = np.argmax(actions)
        state = env.step(action)
        observation = np.expand_dims(np.array(state.observation, dtype=np.float32), axis=0)
        done = state.is_last()
        reward = state.reward
        if reward > 1:
            time.sleep(5)
        score += reward
