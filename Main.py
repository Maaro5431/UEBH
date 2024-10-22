#venv\Scripts\python.exe main.py
from DQN import Agent
import numpy as np
from Game_env import UEBH_env

from utils import plotLearning

if __name__ == "__main__":
    env = UEBH_env()
    num_games = 100
    action_tensor_spec = env.action_spec()
    num_actions = action_tensor_spec.maximum - action_tensor_spec.minimum + 1
    agent = Agent(gamma=0.99, epsilon=1.0, alpha=0.005, input_dims=7, action_size=num_actions, mem_size=1000000,
                  batch_size=64, epsilon_end=0.01)

    scores = []
    eps_hist = []

    for i in range(num_games):
        done = False
        score = 0
        state = env.reset()
        observation = state.observation
        while not done:
            action = agent.choose_action(state)
            state = env.step(action)
            done = state.is_last()
            if done:
                print(str(i)+"__________________________________________________________________________________________________________")
            observation_ = state.observation
            reward = state.reward
            score += reward
            agent.remember(observation, action, reward, observation_, state.step_type)
            observation = observation_
            agent.learn()
        eps_hist.append(agent.epsilon)
        scores.append(score)
        avg_score = np.mean(scores[max(0, i - 100):(i + 1)])
        print('epsilon ', i, 'score %.2f' % score, 'average score %.2f ' % avg_score)

        if i % 10 == 0 and i > 0:
            print("______________________________SAVE______________________________")
            agent.save_model()

    filename = 'UEBH.png'
    x = [i + 1 for i in range(num_games)]
    plotLearning(x,scores, eps_hist, filename)
