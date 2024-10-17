from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abc
import random
from time import sleep
import pygame
import numpy as np
from numpy import str_
import tensorflow as tf
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
from tf_agents.specs import BoundedTensorSpec
import GUI
import UEBH

win = GUI.Win()


class UEBH_env(py_environment.PyEnvironment):

    def __init__(self):
        super().__init__()
        self.game = UEBH.UEBH()
        self.player = self.game.player
        self.village = self.game.village
        self.screen = None

        self.task_complete = True
        self.action_name = ''
        self.die = [0, 0]
        self.current_tower = ''
        self.grid_options = 0

        self._action_spec = BoundedTensorSpec(
            shape=(),  # Scalar (single value for jump)
            dtype=tf.int32,
            minimum=0,  # Minimum jump action (e.g., no jump)
            maximum=27,  # Maximum jump action (e.g., jump)
            name='task')
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(3,),
            dtype=np.int32,
            minimum=0,
            name='observation')
        self._state = 0
        self._episode_ended = False

        # def time_step_spec(self):
        """Describes the `TimeStep` tensors returned by `step()`."""

    # def current_time_step(self):
    #     """Returns the current `TimeStep`."""
    #     return self._current_time_step()

    # def _current_time_step(self):
    #     """Returns the current `TimeStep`."""

    def action_spec(self):

        return self._action_spec

        # nested_action_spec = {
        #     'build_grid': BoundedTensorSpec(
        #         shape=(),  # A vector of length 2 for movement (e.g., x and y direction)
        #         dtype=tf.float32,
        #         minimum=0,  # Minimum bounds for each action dimension
        #         maximum=20,  # Maximum bounds for each action dimension
        #         name='build_action'
        #     ),
        #     'search_grid': BoundedTensorSpec(
        #         shape=(),  # Scalar (single value for jump)
        #         dtype=tf.int32,
        #         minimum=0,  # Minimum jump action (e.g., no jump)
        #         maximum=6,  # Maximum jump action (e.g., jump)
        #         name='search_action'
        #     ),
        #     'task': BoundedTensorSpec(
        #         shape=(),  # Scalar (single value for jump)
        #         dtype=tf.int32,
        #         minimum=0,  # Minimum jump action (e.g., no jump)
        #         maximum=6,  # Maximum jump action (e.g., jump)
        #         name='task'
        #     )
        #
        # }

        # return _action_spec

    def observation_spec(self):
        return self._observation_spec

    def get_observations(self):
        return [self._state, self.player.hit_points, self.village.doubt]#, self.grid_options]

    def _reset(self):
        self.game = UEBH.UEBH()
        self.task_complete = True
        self.player = self.game.player
        self.village = self.game.village
        self._state = 0
        print("\n/////////////////////////////////////////////\nDAY:" + str(self._state + 1))
        self.game.event(self._state)
        # win.reset()
        win.check_box(self.game.time_track_xy[self._state], "X", "black")
        self._episode_ended = False
        return ts.restart(np.array(self.get_observations(), dtype=np.int32))

    def _step(self, act):
        reward = 0
        if self._episode_ended:
            # The last action_name ended the episode. Ignore the current action_name and start
            # a new episode.
            return self._reset()
        if 6 <= act <= 26:
            action_name2 = "build"
        elif 0 <= act <= 5:
            action_name2 = "search"
        elif act == 27:
            action_name2 = "rest"

        if self.task_complete and action_name2 in self.game.get_action_list():
            print("Today you are going to " + action_name2)
            self.action_name = action_name2
        elif not self.action_name == action_name2 or action_name2 not in self.game.get_action_list():
            # print("R1-illegal")
            return ts.transition(
                np.array(self.get_observations(), dtype=np.int32),
                -10, discount=1.0)

        if 0 <= act <= 5:
            for i in [self.game.The_Scar, self.game.Coastal_Caverns, self.game.Halebeard_Peak]:
                if not i.complete:
                    self.player.attack_range = [6]
                    if self.task_complete:
                        print("\nSearching " + i.area_name)
                        if "Sudden Clarity" in i.event:
                            self.player.attack_range.append(4)
                            print(
                                "A flash of insight allows you to sense each beast’s weakness and know just how to "
                                "avoid its attacks. Effect: +1 to your attack range in this region.")
                        if "Madness" in i.event:
                            i.tb_HP += 2
                            print("The beasts grow even more brazen and frenzied as the end of the world draws "
                                  "near. Effect: All beasts in this region have +2 HP")
                        if "Foul Weather" in i.event:
                            self.player.search_range += 2
                            print("Driving rain and fierce thunderstorms scour the landscape making traveling "
                                  "difficult. Effect: You only get two searches per day in this region.")

                        else:
                            self.player.search_range += 3
                        self.die = []
                        self.die.append(random.randint(1, 6))
                        self.die.append(random.randint(1, 6))
                        print("You rolled:" + str(self.die))
                        self.task_complete = False
                        self.grid_options = 0
                        # print("R2- select search")
                        return ts.transition(
                            np.array(self.get_observations(),
                                     dtype=np.int32), 0, discount=1.0)

                    elif act in self.game.box:
                        self.task_complete, result, grid = self.game.search_area(i, act, self.die[0])
                        # self.grid_options = np.concatenate(grid)
                        print("task" + str(self.task_complete))
                        if not (result is None):
                            s_result = search_result(result)
                            print("Result:" + str(s_result))
                            if s_result == "Lair Found":
                                print("\nLair Found " + i.tb)
                                print("DP++")
                                self.player.determination += 1
                                win.check_box(self.player.determination_Coordinates[self.player.determination], "0",
                                              "blue")

                                if self.game.combat_tb(i):
                                    reward += 20
                                else:
                                    self._episode_ended = True

                            elif s_result == "Track Beast":
                                print("\nTrack Beast")
                                i.tb_track += 1
                                if i.tb_track == 3:
                                    print("\nLair Found " + i.tb)
                                    print("DP++")
                                    self.player.determination += 1
                                    win.check_box(self.player.determination_Coordinates[self.player.determination],
                                                  "0", "blue")
                                    self.player.increase_determination_pt()

                                    if self.game.combat_tb(i):
                                        reward += 20
                                    else:
                                        self._episode_ended = True

                            elif s_result == "Encounter":
                                print("\nEncounter")
                                beast_lv = self.game.encounter_chart(result)

                                for lv in i.beasts.keys():
                                    if lv == beast_lv:
                                        encounter = i.beasts[lv]

                                print("A " + encounter + " is attacking!")

                                if self.game.combat(self.game.beast_hp, self.game.beast_attack_range):
                                    print("You have slayed the " + encounter + "\n")
                                else:
                                    self._episode_ended = True

                            elif s_result == "Lair Found and Ambush!":
                                print("\nLair Found and Ambush! " + i.tb)
                                print("DP++")
                                self.player.determination += 1
                                win.check_box(self.player.determination_Coordinates[self.player.determination], "0",
                                              "blue")
                                self.player.attack_range = [6, 5]
                                if self.game.combat_tb(i):
                                    reward += 10
                                else:
                                    self._episode_ended = True

                            print("HP: " + str(self.player.hit_points))
                            if (not i.tb_defeated) and self.task_complete:
                                if self.game.add_doubt(1 + self.village.num_huts_destroyed):
                                    self._episode_ended = True

                        if not self.player.search_range == 0 and not self._episode_ended:
                            self.die.pop(0)
                            if len(self.die) == 0:
                                self.die.append(random.randint(1, 6))
                                self.die.append(random.randint(1, 6))
                                print("You rolled:" + str(self.die) + "\nThe first die:" + str(self.die[0]))
                            else:
                                print("Remaining die:" + str(self.die[0]))
                            # print("R3")
                            return ts.transition(
                                np.array(self.get_observations(),
                                         dtype=np.int32), 1, discount=1.0)
                    else:
                        # print("R4")
                        return ts.transition(
                            np.array(self.get_observations(),
                                     dtype=np.int32), -10, discount=1.0)
                    break


        elif 6 <= act <= 26:
            if not self.task_complete:
                if (act - 6) <= len(self.game.build_options) - 1:
                    self.task_complete, grid  = self.game.build(self.current_tower, act - 6)
                    # self.grid_options = np.concatenate(grid)
                    if not (True in self.village.towers_built.values()):
                        self.village.approval()
                    if not self.task_complete:
                        # print("R5")
                        return ts.transition(
                            np.array(self.get_observations(),
                                     dtype=np.int32), 1, discount=1.0)
                else:
                    # print(self.game.build_options)
                    # print("R6")
                    return ts.transition(
                        np.array(self.get_observations(),
                                 dtype=np.int32), -5, discount=1.0)

            else:
                for i in self.village.towers_built.keys():
                    if not self.village.towers_built[i]:
                        self.current_tower = i
                        break

                self.game.die = random.randint(1, 6)
                self.game.set_build_options(self.current_tower)
                print("You rolled:" + str(self.game.die))
                self.task_complete = False
                self.grid_options = 0
                # print("R7")
                return ts.transition(
                    np.array(self.get_observations(),
                             dtype=np.int32), 1, discount=1.0)

        elif act == 27:
            if self.player.hit_points == 10:
                reward = -1
            self.game.rest()

        print("HP: " + str(self.player.hit_points) + "\nDoubt: " + str(self.village.doubt))
        # sleep(1)
        if self._state == 13 or self.village.doubt >= 18:
            self._episode_ended = True
        elif not self._episode_ended:
            self._state += 1
            print("\n_____________________________________\nDAY:" + str(self._state + 1))
            self.game.event(self._state)
            win.check_box(self.game.time_track_xy[self._state], "X", "black")

        if self._episode_ended or self._state == 14:
            score = self.game.calc_score(False)
            reward += self._state + score - (self.village.doubt)
            # print("R8")
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXX GAME OVER XXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            return ts.termination(
                np.array(self.get_observations(), dtype=np.int32),
                reward)
        else:
            reward += self._state - (self.village.doubt)
            # print("R9")
            return ts.transition(
                np.array(self.get_observations(), dtype=np.int32),
                reward, discount=1.0)


def search_result(result):
    if 1 <= result <= 10:
        return "Lair Found"
    elif 11 <= result <= 99:
        return "Track Beast"
    elif 100 <= result <= 555 or -555 <= result <= -1:
        return "Encounter"
    elif result == 0:
        return "Lair Found and Ambush!"
