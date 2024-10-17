from __future__ import absolute_import, division, print_function
import os
import base64
import numpy
from time import sleep

from Game import UEBH_env

# Keep using keras-2 (tf-keras) rather than keras-3 (keras).
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import PIL.Image
import tensorflow as tf

from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.agents.dqn import dqn_agent
from tf_agents.drivers import py_driver
from tf_agents.environments import suite_gym
from tf_agents.environments import tf_py_environment
from tf_agents.eval import metric_utils
from tf_agents.metrics import tf_metrics
from tf_agents.networks import sequential
from tf_agents.policies import py_tf_eager_policy
from tf_agents.policies import random_tf_policy
from tf_agents.replay_buffers import reverb_replay_buffer
from tf_agents.replay_buffers import reverb_utils
from tf_agents.trajectories import trajectory
from tf_agents.specs import tensor_spec
from tf_agents.utils import common

# Set up parameters
num_iterations = 100  # @param {type:"integer"}

initial_collect_steps = 150  # @param {type:"integer"}
collect_steps_per_iteration = 1  # @param {type:"integer"}
replay_buffer_max_length = 100000  # @param {type:"integer"}

batch_size = 64  # @param {type:"integer"}
learning_rate = 1e-3  # @param {type:"number"}
log_interval = 200  # @param {type:"integer"}

num_eval_episodes = 100  # @param {type:"integer"}
eval_interval = 1000  # @param {type:"integer"}

# Set up the environment (UEBH_env needs to be defined)
env = UEBH_env()
env.reset()

# Wrap the environment for TensorFlow
train_env = tf_py_environment.TFPyEnvironment(env)
eval_env = tf_py_environment.TFPyEnvironment(env)

# Q-Network parameters
fc_layer_params = (100, 50)
action_tensor_spec = train_env.action_spec()
num_actions = action_tensor_spec.maximum - action_tensor_spec.minimum + 1


# Define a helper function to create Dense layers configured with the right
# activation and kernel initializer.
def dense_layer(num_units):
    return tf.keras.layers.Dense(
        num_units,
        activation=tf.keras.activations.relu,
        kernel_initializer=tf.keras.initializers.VarianceScaling(
            scale=2.0, mode='fan_in', distribution='truncated_normal'))


# QNetwork consists of a sequence of Dense layers followed by a dense layer
# with `num_actions` units to generate one q_value per available action as
# its output.

dense_layers = [dense_layer(num_units) for num_units in fc_layer_params]
q_values_layer = tf.keras.layers.Dense(
    num_actions,
    activation=None,
    kernel_initializer=tf.keras.initializers.RandomUniform(minval=-0.03, maxval=0.03),
    bias_initializer=tf.keras.initializers.Constant(-0.2))
q_net = sequential.Sequential(dense_layers + [q_values_layer])

optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

train_step_counter = tf.Variable(0)

agent = dqn_agent.DqnAgent(
    train_env.time_step_spec(),
    train_env.action_spec(),
    q_network=q_net,
    optimizer=optimizer,
    td_errors_loss_fn=common.element_wise_squared_loss,
    train_step_counter=train_step_counter)

agent.initialize()

eval_policy = agent.policy
collect_policy = agent.collect_policy

random_policy = random_tf_policy.RandomTFPolicy(train_env.time_step_spec(),
                                                train_env.action_spec())


# Function to collect data
def collect_step(environment, policy, buffer):
    time_step = environment.current_time_step()
    action_step = policy.action(time_step)
    next_time_step = environment.step(action_step.action)
    traj = trajectory.from_transition(time_step, action_step, next_time_step)
    # Add trajectory to the replay buffer
    traj = tf.nest.map_structure(tf.stop_gradient, traj)
    print(traj)
    buffer.add_batch(traj)


# Replay buffer to store collected data
replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    data_spec=agent.collect_data_spec,
    batch_size=train_env.batch_size,
    max_length=replay_buffer_max_length)

# Initial data collection
for _ in range(initial_collect_steps):
    # collect_step(train_env, random_tf_policy.RandomTFPolicy(train_env.time_step_spec(), train_env.action_spec()),
    #              replay_buffer)
    collect_step(train_env, random_policy, replay_buffer)

# Dataset generates trajectories with the replay buffer
dataset = replay_buffer.as_dataset(
    num_parallel_calls=3,
    sample_batch_size=batch_size,
    num_steps=2).prefetch(3)

iterator = iter(dataset)

# (Optional) Optimize by wrapping some of the code in a graph using TF function.
agent.train = common.function(agent.train)

# Reset the train step
agent.train_step_counter.assign(0)


# Evaluate the agent's policy once before training.
def compute_avg_return(environment, policy, num_episodes=10):
    total_return = 0.0
    for _ in range(num_episodes):
        time_step = environment.reset()

        episode_return = 0.0
        count = 0
        previous_act = 7
        while not time_step.is_last():
            action_step = policy.action(time_step)
            time_step = environment.step(action_step.action)
            if action_step == previous_act:
                count += 1
                if count == 50:
                    print("GOT STUCK")
                    break
            previous_act = action_step
            episode_return += time_step.reward

        print(time_step)
        print(time_step.reward)
        total_return += episode_return

    avg_return = total_return / num_episodes
    return avg_return.numpy()[0]


dataset = replay_buffer.as_dataset(
    num_parallel_calls=3,
    sample_batch_size=batch_size,
    num_steps=2).prefetch(3)

agent.train = common.function(agent.train)
agent.train_step_counter.assign(0)

avg_return = compute_avg_return(eval_env, agent.policy, num_eval_episodes)
returns = [avg_return]
sleep(10)
print("\n\nBegin training.")

time_step = train_env._reset()

# Create a driver to collect experience.F
collect_driver = py_driver.PyDriver(
    env,
    py_tf_eager_policy.PyTFEagerPolicy(
        agent.collect_policy, use_tf_function=True),
    [],
    max_steps=collect_steps_per_iteration)
# Training loop
print("Begin training")
for _ in range(num_iterations):
    train_env._reset()
    print(time_step)

    # Sample a batch of data from the buffer and update the agent's network.
    experience, unused_info = next(iterator)
    # print("Experience data type:", type(experience))
    # print("Experience content:", experience)

    experience_tensor = tf.nest.map_structure(tf.convert_to_tensor, experience)
    # train_loss = agent.train(experience_tensor).loss

    step = agent.train_step_counter.numpy()
    print(_)

    if step % log_interval == 0:
        print('step = {0}:  '.format(step))

    # if step % log_interval == 0:
    #     print('step = {0}: loss = {1}'.format(step, train_loss))

    if step % eval_interval == 0:
        avg_return = compute_avg_return(eval_env, agent.policy, num_eval_episodes)
        print('step = {0}: Average Return = {1}'.format(step, avg_return))
        returns.append(avg_return)

print("Training completed.")
