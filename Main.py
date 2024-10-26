#venv\Scripts\python.exe main.py
from DQN import Agent
import numpy as np
import matplotlib.pyplot as plt
from Game_env import UEBH_env
from utils import plotLearning

# Create a single figure and axis at the start
fig, ax = plt.subplots(figsize=(10, 6))


def plot_illegal_actions_score(illegal_actions, score):
    episodes = range(1, len(illegal_actions) + 1)

    # Plot both illegal actions and score
    ax.clear()  # Clear previous plot data to save memory
    ax.plot(episodes, illegal_actions, label='Illegal Actions', color='red', marker='o')
    ax.plot(episodes, score, label='Score', color='blue', marker='x')
    ax.set_title('Illegal Actions and Scores Over Training Episodes')
    ax.set_xlabel('Episode')
    ax.set_ylabel('Count / Score')
    ax.grid(True)
    ax.legend()
    fig.savefig("illegal_actions_and_scores_plot.png")

    # Plot illegal actions only
    ax.clear()  # Clear data again for the next plot
    ax.plot(episodes, illegal_actions, label='Illegal Actions', color='red', marker='o')
    ax.set_title('Illegal Actions Over Training Episodes')
    ax.set_xlabel('Episode')
    ax.set_ylabel('Illegal Actions Count')
    ax.grid(True)
    ax.legend()
    fig.savefig("illegal_actions_only_plot.png")


if __name__ == "__main__":
    env = UEBH_env()
    num_games = 1000
    action_tensor_spec = env.action_spec()
    num_actions = action_tensor_spec.maximum - action_tensor_spec.minimum + 1
    agent = Agent(gamma=0.999, epsilon=1.0, alpha=0.9, input_dims=7, action_size=num_actions, mem_size=10000,
                  batch_size=64, epsilon_end=0.01)

    scores = []
    eps_hist = []
    illegal_action_list = []
    filename = 'UEBH.png'

    for i in range(num_games):
        done = False
        score = 0
        illegal_act_count =0
        state = env.reset()
        observation = state.observation
        while not done:
            action = agent.choose_action(state)
            state = env.step(action)
            done = state.is_last()
            if done:
                illegal_action_list.append(illegal_act_count)
                print("__________________________________________________________________________________________________________")
            observation_ = state.observation
            reward = state.reward
            if reward in [0,-3]:
                illegal_act_count+=1
            score += reward
            agent.remember(observation, action, reward, observation_, state.step_type)
            observation = observation_
            agent.learn()
        eps_hist.append(agent.epsilon)
        scores.append(score)
        avg_score = np.mean(scores[max(0, i - 100):(i + 1)])
        print('Game: ', i, 'score %.2f' % score, 'average score %.2f ' % avg_score)

        if i % 10 == 0 and i > 0:
            print("______________________________SAVE______________________________")
            agent.save_model()

            x = [j + 1 for j in range(i + 1)]
            plotLearning(x, scores, eps_hist, filename)
            plot_illegal_actions_score(illegal_action_list, scores)

    x = [i + 1 for i in range(num_games)]
    plotLearning(x, scores, eps_hist, filename)
