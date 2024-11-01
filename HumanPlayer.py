import numpy as np
import GUI
from Game_env import UEBH_env
from tf_agents.environments import tf_py_environment

env = UEBH_env()
tf_env = tf_py_environment.TFPyEnvironment(env)
window = GUI.Win(True)

running = True
action_spec = tf_env.action_spec()
task_act = np.array(0, dtype=np.int32)

time_step = tf_env.reset()
cumulative_reward = time_step.reward
act_array = []
while not time_step.is_last():

    # running = GUI.get_py_game_event()
    # window.mark()

    print("Select action by entering corresponding number.")
    count = 0
    while True:
        index = int(window.input_number_box())
        if index in range(0, 28):
            break
        else:
            print("Value not in range")

    task_act = np.array(index, dtype=np.int32)
    time_step = tf_env.step(task_act)
    GUI.update_window()
    cumulative_reward += time_step.reward

GUI.close_win()

print('Final Reward = ', cumulative_reward[0])
