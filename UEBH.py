import random
import GUI
from GUI import Storyline

window = GUI.Win(False)

story = Storyline()


def attack_tower(tower, coordinates1):
    rows = len(tower)
    for i in range(rows):
        cols = len(tower[i])
        for j in range(cols):
            if tower[i][j] not in (0, 7):
                tower[i][j] = 0
                window.check_box(coordinates1[i][j], "X", "red")
                return tower


def get_build_options(die, tower):
    options = []
    if any(die in i for i in tower):
        # print("Die:" + str(d))
        story.write_line("Die:" + str(die))
        rows = len(tower)
        for r in range(rows):
            cols = len(tower[r])
            for c in range(cols):
                if tower[r][c] == die:
                    # Check right
                    if c < cols - 1 and tower[r][c + 1] == 0:
                        options.append([r, c + 1])
                    # Check left
                    if c > 0 and tower[r][c - 1] == 0:
                        options.append([r, c - 1])
                    # Check up
                    if r > 0 and tower[r - 1][c] == 0:
                        options.append([r - 1, c])
                    # Check down
                    if r < rows - 1 and tower[r + 1][c] == 0:
                        options.append([r + 1, c])


    else:
        # print("New num:" + str(d))
        story.write_line("New num:" + str(die))
        rows = len(tower)
        for r in range(rows):
            cols = len(tower[r])
            for c in range(cols):
                if tower[r][c] == 0:
                    available = True

                    # Check right
                    if c < cols - 1 and tower[r][c + 1] not in [0, 7]:
                        available = False
                    # Check left
                    elif c > 0 and tower[r][c - 1] not in [0, 7]:
                        available = False
                    # Check up
                    elif r > 0 and tower[r - 1][c] not in [0, 7]:
                        available = False
                    # Check down
                    elif r < rows - 1 and tower[r + 1][c] not in [0, 7]:
                        available = False

                    if available:
                        options.append([r, c])

    return options


class UEBH():
    def __init__(self):
        self.die = 0
        self.day = 0
        self.player = Player()
        self.village = Village()
        self.Coastal_Caverns = Area("Coastal Caverns")
        self.Halebeard_Peak = Area("Halebeard Peak")
        self.The_Scar = Area("The Scar")
        self.time_track = ["E", " ", "!", "E", " ", "!", "E", " ", "!", "E", " ", "!", "E", "D"]
        self.time_track_xy = [[602, 41], [583, 41], [583, 57], [583, 76], [602, 85], [621, 86], [621, 103], [602, 107],
                              [583, 119], [602, 129], [621, 138], [621, 157], [602, 164], [583, 167]]
        self.search_options = [0, 1, 2, 3, 4, 5]
        self.build_options = None
        self.grid = []
        self.beast_attack_range = []


    def set_build_options(self, tn):
        t, coordanates = self.village.towers[tn]
        self.build_options = get_build_options(self.die, t)

    def rest(self):
        if self.player.hit_points > 8:
            # print("HP= 10")
            story.write_line("HP= 10")
            self.player.hit_points = 10
        else:
            # print(2 * "HP++")
            story.write_line(str(2 * "HP++"))
            for i in range(2):
                window.check_box(self.player.HP_Coordinates[self.player.hit_points + i], "X", "green")
            self.player.increase_hp(2)
        return self.add_doubt(1)

    def reset_event(self):
        self.Coastal_Caverns.event = []
        self.The_Scar.event = []
        self.Halebeard_Peak.event = []

    def tb_attack(self, area2):
        # while area2.tb_defeated:  #terrible beast defeated
        #     area2 = select_area()

        if not area2.tb_defeated:
            if area2.area_name == "Coastal Caverns":
                t_name = "Eastern Tower"
            elif area2.area_name == "Halebeard Peak":
                t_name = "Southern Tower"
            else:
                t_name = "South Western Tower"
            # print("The " + area2.tb, " is attacking the " + t_name)
            story.write_line("".join(["The " + area2.tb, " is attacking the " + t_name]))
            if self.village.towers_built[t_name]:
                tower, coordinates = self.village.towers[t_name]
                die = random.randint(1, 6)
                if die == 2:
                    self.village.towers[t_name] = attack_tower(tower, coordinates), coordinates
                    # print("The " + t_name + "took a hit!")
                    story.write_line("".join(["The " + t_name + "took a hit!"]))
                elif die in [3, 4, 5]:
                    for i in range(2):
                        self.village.towers[t_name] = attack_tower(tower, coordinates), coordinates
                    # print("The " + t_name + "took two hit's!")
                    story.write_line("".join(["The " + t_name + "took two hit's!"]))
                elif die == 6:
                    rows = len(tower)
                    for i in range(rows):
                        cols = len(tower[i])
                        for j in range(cols):
                            if tower[i][j] != 7:
                                tower[i][j] = 0
                                window.check_box(coordinates[i][j], "X", "white")

                    # print("The " + t_name + "was destroyed!")
                    story.write_line("".join(["The " + t_name + "was destroyed!"]))
                    self.village.towers[t_name] = (tower, coordinates)
                    self.village.towers_built[t_name] = False
                else:
                    # print("The " + t_name + "took no damage")
                    story.write_line("".join(["The " + t_name + "took no damage"]))

                for i in tower:
                    story.write_line(i)
            else:
                # print("A hut was destroyed!")
                story.write_line("A hut was destroyed!")

                for i, (not_destroyed, coordinates) in enumerate(self.village.huts.items(), start=1):
                    if not_destroyed:
                        window.check_box(coordinates, "X", "red")
                        self.village.huts[i] = (False, coordinates)
                        self.village.num_huts_destroyed += 1
                        self.add_doubt(2 * self.village.num_huts_destroyed)
                        break

    def set_event(self):
        event_list = ["Sudden Clarity", "Foul Weather", "Madness"]
        for i in event_list:
            d = self.roll_die()[0]
            if d in [1, 2]:
                self.Halebeard_Peak.event.append(i)
                if (i == "Madness") and "Foul Weather" in self.Halebeard_Peak.event and not self.Halebeard_Peak.tb_defeated:
                    # print(
                    #     "A region is affected by both Foul Weather and Madness at the same time, the Terrible Beast in "
                    #     "this region is overcome with rage and immediately descends into the valley to assault the "
                    #     "village.")
                    story.write_line(
                        "A region is affected by both Foul Weather and Madness at the same time, the Terrible Beast in "
                        "this region is overcome with rage and immediately descends into the valley to assault the "
                        "village.")
                    self.tb_attack(self.Halebeard_Peak)
            elif d in [3, 4]:
                self.Coastal_Caverns.event.append(i)
                if (
                        i == "Madness") and "Foul Weather" in self.Coastal_Caverns.event and not self.Coastal_Caverns.tb_defeated:
                    # print(
                    #     "A region is affected by both Foul Weather and Madness at the same time, the Terrible Beast in "
                    #     "this region is overcome with rage and immediately descends into the valley to assault the "
                    #     "village.")
                    story.write_line(
                        "A region is affected by both Foul Weather and Madness at the same time, the Terrible Beast in "
                        "this region is overcome with rage and immediately descends into the valley to assault the "
                        "village.")
                    self.tb_attack(self.Coastal_Caverns)
            elif d in [5, 6]:
                self.The_Scar.event.append(i)
                if (
                        i == "Madness") and "Foul Weather" in self.The_Scar.event and not self.The_Scar.tb_defeated:
                    # print(
                    #     "A region is affected by both Foul Weather and Madness at the same time, the Terrible Beast in "
                    #     "this region is overcome with rage and immediately descends into the valley to assault the "
                    #     "village.")
                    story.write_line(
                        "A region is affected by both Foul Weather and Madness at the same time, the Terrible Beast in "
                        "this region is overcome with rage and immediately descends into the valley to assault the "
                        "village.")
                    self.tb_attack(self.The_Scar)

    def event(self, day):
        if self.time_track[day] == "!":
            area = self.select_area()
            while area.tb_defeated:
                area = self.select_area()
            self.tb_attack(area)

        self.reset_event()
        if self.time_track[day] == "E":
            self.set_event()

    def roll_die(self):
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        if self.player.determination > 0:
            if random.choice([True, False]):
                window.check_box(self.player.determination_Coordinates[self.player.determination], "0", "white")
                self.player.determination = -1
                die1 = random.randint(1, 6)
                die2 = random.randint(1, 6)
                # print(" New role DP -1 ")
                story.write_line(" New role DP -1 ")

        return [die1, die2]

    def encounter_chart(self, val):
        global attack_range, beast_attack_range, beast_hp
        encounter_lv = 0
        if (555 >= val >= 500) or (-401 >= val >= -555):
            encounter_lv = 4
        elif (499 >= val >= 400) or (-301 >= val >= -400):
            encounter_lv = 3
        elif (399 >= val >= 300) or (-201 >= val >= -300):
            encounter_lv = 2
        elif (299 >= val >= 200) or (-101 >= val >= -300):
            encounter_lv = 1
        elif (199 >= val >= 100) or (-1 >= val >= -100):
            new_roll = random.randint(1, 6)
            if new_roll in [1, 2]:
                encounter_lv = 1
            elif new_roll in [3, 4]:
                encounter_lv = 2
            elif new_roll == 5:
                encounter_lv = 2
            else:
                encounter_lv = 2

        if encounter_lv == 1:
            self.player.attack_range = [5, 6]
            self.beast_attack_range = [1]
            self.beast_hp = 2
        elif encounter_lv == 2:
            self.player.attack_range = [5, 6]
            self.beast_attack_range = [1, 2]
            self.beast_hp = 2
        elif encounter_lv == 3:
            self.player.attack_range = [5, 6]
            self.beast_attack_range = [1, 2]
            self.beast_hp = 3
        elif encounter_lv == 4:
            self.player.attack_range = [6]
            self.beast_attack_range = [1, 2, 3]
            self.beast_hp = 3

        return encounter_lv

    def build(self, tn, act):
        filled = True
        # print(tn)
        story.write_line(tn)
        t, coordinates = self.village.towers[tn]
        d = self.die
        options = self.build_options
        tower_index = options[act]
        c = tower_index[1]
        r = tower_index[0]

        tower_coordinate = coordinates[r][c]
        window.check_box(tower_coordinate, str(d), "black")

        t[r][c] = d
        self.village.towers[tn] = (t, coordinates)
        story.write_line("---------------------")
        # print("---------------------")
        for i in t:
            # print(i)
            story.write_line(i)

        d = self.roll_die()
        d = d[0]
        options = get_build_options(d, t)

        if not options:
            self.village.towers_built[tn] = True
            # print("No available blocks.\n=======================")
            story.write_line("No available blocks.\n=======================")
            for r1, row in enumerate(t):
                for c1, val in enumerate(row):
                    if val == 0:
                        tower_coordinate = coordinates[r1][c1]
                        window.check_box(tower_coordinate, "X", "black")
                        filled = False

            if filled:
                # print("DP++")
                story.write_line("DP++")
                self.player.determination += 1
                window.check_box(self.player.determination_Coordinates[self.player.determination], "0", "blue")

            self.build_options = []
            self.die = 0
            return True, t

        else:
            # print('A avalabel blocks:\n' + str(options))
            story.write_line("".join(['A avalabel blocks:\n' + str(options)]))
            self.die = d
        self.build_options = options
        return False, t

    def select_tower(self):
        choice = [key for key, built in self.village.towers_built.items() if not built]

        tower_name = random.choice(choice)  # Select Tower

        self.village.towers_built[tower_name] = True

        return tower_name

    def combat(self, beast_hp2, beast_attack_range2):
        attack_range2 = self.player.attack_range
        while beast_hp2 > 0:
            die1 = self.roll_die()
            if die1[0] == 6 and die1[1] == 6:
                # print("CRITICAL HIT! +1 additional damage to beast")
                story.write_line("CRITICAL HIT! +1 additional damage to beast")
                critical_hit = 1
                self.player.increase_determination_pt()
            else:
                critical_hit = 0
            for d in die1:
                if d in attack_range2:
                    # print("attack beast")
                    story.write_line("attack beast")

                    beast_hp2 -= 1 + critical_hit
                elif d in beast_attack_range2:
                    # print("take damage")
                    story.write_line("take damage")
                    self.player.hit_points -= 1
                    xy = self.player.HP_Coordinates[self.player.hit_points]
                    window.check_box(xy, "X", "black")
                    if self.player.hit_points == 1:
                        # print("DP++")
                        story.write_line("DP++")
                        self.player.determination += 1
                        window.check_box(self.player.determination_Coordinates[self.player.determination], "0", "blue")

            if self.player.hit_points <= 0:
                break

        if self.player.hit_points < 1:
            xy = self.player.HP_Coordinates[self.player.hit_points]
            window.check_box(xy, "X", "black")
            # print("Your strength evaporates and you slump to the ground in defeat. The shock of the final blow is,
            # \n " "surprisingly, not what draws your focus. It is the relief you feel. For the first time in what
            # must be \n" "years the tension in your back fades and a warm serenity washes over you as the world
            # turns black")
            story.write_line(
                "Your strength evaporates and you slump to the ground in defeat. The shock of the final blow is,\n "
                "surprisingly, not what draws your focus. It is the relief you feel. For the first time in what must be \n"
                "years the tension in your back fades and a warm serenity washes over you as the world turns black")
            return False

        else:
            # print("Victory")
            story.write_line("Victory")
            return True

    def combat_tb(self, area1):
        terrible_beast_ar = [1, 2, 3]
        if self.combat(area1.tb_HP, terrible_beast_ar):
            window.check_box(area1.tb_hp_coordinates, "/////////////////////////////////", "red")
            area1.tb_defeated = True
            area1.complete = True
            self.village.approval()
            return True
        else:
            return False

    def calc_score(self, win):
        score = 0
        if self.Coastal_Caverns.tb_defeated:
            score += 50
        if self.The_Scar.tb_defeated:
            score += 50
        if self.Halebeard_Peak.tb_defeated:
            score += 50

        score += sum(15 for i in self.village.towers_built.values() if i)
        if win:
            if self.village.huts == 0:
                score += 50
            score += 5 * self.day
            score += 2 * self.player.hit_points
            score += (18 - self.village.doubt)
        # print("Your score is " + str(score))
        story.write_line("".join(["Your score is " + str(score)]))
        return score

    def add_doubt(self, n):
        n1 = self.village.doubt
        self.village.doubt += n
        # Limit the loop to the valid range
        for d in range(min(n, 18 - n1)):
            window.check_box(self.village.xy_doubt[n1 + d], "X", "black")

        # print("Doubt increased by " + str(n))
        story.write_line("".join(["Doubt increased by ", str(n)]))
        if self.village.doubt >= 18:

            self.calc_score(False)
            # print("You have lost the villagers’ trust")
            # print("A crowd gathers in the village square. The knot in your stomach grows as you pick out the faces of "
            #       "your most vocal critics among the mob. Under a hail of stones you are chased out of the village "
            #       "into the unforgiving wilderness. You hear the thunder of hooves as a contingent of the Blazing "
            #       "Star Regiment races into the valley. Injured as you are, you realize escape is impossible.")
            story.write_line(
                "You have lost the villagers’ trust.\nA crowd gathers in the village square. The knot in your stomach grows as you pick out the faces of "
                "your most vocal critics among the mob. Under a hail of stones you are chased out of the village "
                "into the unforgiving wilderness. You hear the thunder of hooves as a contingent of the Blazing "
                "Star Regiment races into the valley. Injured as you are, you realize escape is impossible.")
            return True
        else:
            return False

    def select_area(self):
        a_name = ["Coastal Caverns", "The Scar", "Halebeard Peak"]

        a = random.choice(a_name)  # int(input("Coastal Caverns-1 the Halebeard Peak-2, The Scar-3"))
        if a == "Coastal Caverns":
            area1 = self.Coastal_Caverns
        elif a == "Halebeard Peak":
            area1 = self.Halebeard_Peak
        else:
            area1 = self.The_Scar
        return area1

    def search_area(self, area, action_num, die):
        grid_num = area.grids_searched
        self.search_options.remove(action_num)
        area.searchBox[grid_num][action_num] = die
        coordinates2 = area.searchBox_coordinates[grid_num][action_num]

        window.check_box(coordinates2, str(die), "black")
        # print(
        #     "Grid:\n " + str(area.searchBox[grid_num][:3]) + "\n-" + str(area.searchBox[grid_num][3:]))
        story.write_line(
            str("Grid:\n " + str(area.searchBox[grid_num][:3]) + "\n-" + str(area.searchBox[grid_num][3:])))

        if not (0 in area.searchBox[grid_num]):
            # print('Grid complete.')
            story.write_line('Grid complete.')
            self.player.search_range -= 1
            # print(self.player.search_range)
            story.write_line(str(self.player.search_range))
            area.grids_searched += 1
            self.search_options = [0, 1, 2, 3, 4, 5]
            if area.grids_searched == 6:
                area.complete = True
            result = area.searchBox[grid_num][0] * 100 + area.searchBox[grid_num][1] * 10 + area.searchBox[grid_num][
                2] - area.searchBox[grid_num][3] * 100 - area.searchBox[grid_num][4] * 10 - area.searchBox[grid_num][5]
            if self.player.search_range == 0:
                story.write_line("Search complete.")
                return True, result, area.searchBox[grid_num]
            else:
                return False, result, area.searchBox[grid_num]

        return False, None, area.searchBox[grid_num]
        #
        # for grid in grid_num:
        #     b = [0, 1, 2, 3, 4, 5]
        #     for lv in range(3):
        #         print("You rolled:" + str(die))

        # not_legal = True
        #
        # while not_legal:
        #     print("Legal blocks include:")
        #     for i in b:
        #         print(i)
        #     print("Enter the corresponding number to place " + (str(die1[0])))
        #     input = int(window.input_number_box())
        #     if input in b:
        #         b1 = input
        #         b.remove(b1)
        #         while not_legal:
        #             print("Legal blocks include:")
        #             for i in b:
        #                 print(i)
        #             print("Enter the corresponding number to place " + (str(die1[1])))
        #             input = int(window.input_number_box())
        #             if input in b:
        #                 b2 = input
        #                 b.remove(b2)
        #                 not_legal = False

        # box1 = b1   # Agent selects next box in the grid
        # box2 = b2
        #         box1 = random.choice(b)
        #         b.remove(box1)
        #         box2 = random.choice(b)
        #         b.remove(box2)
        #
        #         area.searchBox[grid][box1] = die1[0]
        #         coordinates2 = area.searchBox_coordinates[grid][box1]
        #
        #         window.check_box(coordinates2, str(die1[0]), "black")
        #
        #         area.searchBox[grid][box2] = die1[1]
        #         coordinates2 = area.searchBox_coordinates[grid][box2]
        #
        #         window.check_box(coordinates2, str(die1[1]), "black")
        #         print("Grid:\n " + str(area.searchBox[grid][:3]) + "\n-" + str(
        #             area.searchBox[grid][3:]) + "\nDie:" + str(
        #             die1))
        #
        #     GUI.update_window()
        #
        #     area.grids_searched += 1
        #     if area.grids_searched == 6:
        #         area.complete = True
        #
        #     result = area.searchBox[grid][0] * 100 + area.searchBox[grid][1] * 10 + area.searchBox[grid][2] \
        #              - area.searchBox[grid][3] * 100 - area.searchBox[grid][4] * 10 - area.searchBox[grid][5]
        #     s_result = search_result(result)
        #     print("Result:" + str(result))
        #
        #     if s_result == "Lair Found":
        #         print("\nLair Found " + area.tb)
        #         print("DP++")
        #         self.player.determination += 1
        #         window.check_box(self.player.determination_Coordinates[self.player.determination], "0", "blue")
        #         if self.combat_tb(terrible_beast_hp, ar, area):
        #             return True
        #         else:
        #             return False
        #
        #     elif s_result == "Track Beast":
        #         print("\nTrack Beast")
        #         area.tb_track += 1
        #         if area.tb_track == 3:
        #             print("\nLair Found " + area.tb)
        #             print("DP++")
        #             self.player.determination += 1
        #             window.check_box(self.player.determination_Coordinates[self.player.determination], "0", "blue")
        #             self.player.increase_determination_pt()
        #             if self.combat_tb(terrible_beast_hp, ar, area):
        #                 return True
        #             else:
        #                 return False
        #
        #     elif s_result == "Encounter":
        #         print("\nEncounter")
        #         beast_lv, ar, beast_ar, beast_h = encounter_chart(result)
        #         if "Madness" in area.event:
        #             beast_h += 2
        #         if "Sudden Clarity" in area.event:
        #             ar.append(4)
        #         for lv in area.beasts.keys():
        #             if lv == beast_lv:
        #                 encounter = area.beasts[lv]
        #         print("A " + encounter + " is attacking!")
        #
        #         if self.combat(ar, beast_ar, beast_h):
        #             print("You have slayed the " + encounter + "\n")
        #         else:
        #             return False
        #
        #     elif s_result == "Lair Found and Ambush!":
        #         print("\nLair Found and Ambush! " + area.tb)
        #         print("DP++")
        #         self.player.determination += 1
        #         window.check_box(self.player.determination_Coordinates[self.player.determination], "0", "blue")
        #         ar.append(5)
        #         if self.combat_tb(terrible_beast_hp, ar, area):
        #             return True
        #         else:
        #             return False
        #     print("HP: " + str(self.player.hit_points))
        # return True

    def end_game(self):
        if self.Coastal_Caverns.tb_defeated and self.The_Scar.tb_defeated and self.Halebeard_Peak.tb_defeated:
            # print("You have defeated all three Terrible Beasts - Win")
            # print("A calm wind carries the distant sound of brass horns as the Blazing Star Regiment begins its final "
            #       "approach. A solemn crowd gathers in the village square to watch the proceedings. You have proven "
            #       "your worth. The village elders nod to each other. There is a sense of nervousness and excitement "
            #       "in the crowd. Sipporos leads you into a nearby hut and closes the heavy door flap. In the darkness "
            #       "you hear the footsteps of armored soldiers outside the hut.")
            story.write_line(
                "You have defeated all three Terrible Beasts - Win.\nA calm wind carries the distant sound of brass horns as the Blazing Star Regiment begins its final "
                "approach. A solemn crowd gathers in the village square to watch the proceedings. You have proven "
                "your worth. The village elders nod to each other. There is a sense of nervousness and excitement "
                "in the crowd. Sipporos leads you into a nearby hut and closes the heavy door flap. In the darkness "
                "you hear the footsteps of armored soldiers outside the hut.")
            return self.calc_score(True)

        if self.time_track[self.day] == "D":
            self.calc_score(False)
            # print("You have run out of time - Loss")
            # print("The sound of soldiers and horses fills the air as the Blazing Star Regiment assembles outside the "
            #       "village walls. A nervous crowd gathers in the village square to watch the proceedings. The elders "
            #       "consider you to have broken your promise. Furious that you have wasted their time and endangered "
            #       "the lives of the entire village, they cast you out of the village and into the waiting hands of "
            #       "the Blazing Star Regiment. Escape is impossible")
            story.write_line(
                "You have run out of time - Loss.\nThe sound of soldiers and horses fills the air as the Blazing Star Regiment assembles outside the "
                "village walls. A nervous crowd gathers in the village square to watch the proceedings. The elders "
                "consider you to have broken your promise. Furious that you have wasted their time and endangered "
                "the lives of the entire village, they cast you out of the village and into the waiting hands of "
                "the Blazing Star Regiment. Escape is impossible")
            return self.calc_score(False)
        return self.calc_score(False)

    def get_action_list(self):
        action_list = ["search", "rest"]
        if False in self.village.towers_built.values():
            action_list.append("build")
        return action_list


class Village:
    def __init__(self):
        self.num_huts_destroyed = 0
        self.huts = {1: (True, [256, 711]), 2: (True, [301, 724]), 3: (True, [337, 748]), 4: (True, [290, 760]),
                     5: (True, [248, 746]), 6: (True, [417, 639]), 7: (True, [452, 655]), 8: (True, [483, 672]),
                     9: (True, [545, 699])}
        self.doubt = 0
        self.xy_doubt = [[224, 99], [235, 95], [247, 87], [259, 82], [272, 79], [284, 73], [233, 108], [246, 101],
                         [257, 97], [269, 91], [281, 87], [294, 82], [242, 119], [256, 114], [268, 106], [279, 102],
                         [291, 95], [304, 92]]
        self.elders_approval = {"Epiphoros": False, "Sipporos": False, "Nikandros": False}
        self.towers_built = {"Eastern Tower": False, "Southern Tower": False, "South Western Tower": False}
        self.towers = {"Eastern Tower": ([[7, 7, 0, 7],
                                          [7, 0, 0, 7],
                                          [0, 0, 0, 7],
                                          [0, 0, 0, 7],
                                          [0, 0, 0, 0],
                                          [0, 0, 0, 0],
                                          [0, 7, 0, 0]],
                                         [[7, 7, [120, 648], 7],
                                          [7, [104, 666], [120, 666], 7],
                                          [[87, 681], [104, 681], [120, 681], 7],
                                          [[87, 697], [104, 697], [120, 697], 7],
                                          [[87, 712], [104, 712], [120, 712], [136, 712]],
                                          [[87, 728], [104, 728], [120, 728], [136, 728]],
                                          [[87, 744], 7, [120, 744], [136, 744]]]),

                       "Southern Tower": ([[7, 0, 0, 7],
                                           [7, 0, 0, 7],
                                           [7, 0, 0, 7],
                                           [7, 0, 0, 0],
                                           [7, 0, 0, 0],
                                           [0, 0, 0, 0],
                                           [0, 0, 0, 0]],
                                          [[7, [312, 517], [329, 517], 7],
                                           [7, [312, 533], [329, 533], 7],
                                           [7, [312, 549], [329, 549], 7],
                                           [7, [312, 566], [329, 566], [346, 566]],
                                           [7, [312, 581], [329, 581], [346, 581]],
                                           [[298, 597], [312, 597], [329, 597], [346, 597]],
                                           [[298, 613], [312, 613], [329, 613], [346, 613]]],
                                          ),
                       "South Western Tower": ([[7, 0, 0],
                                                [7, 0, 0],
                                                [0, 0, 0],
                                                [0, 0, 0],
                                                [0, 7, 0],
                                                [0, 7, 0],
                                                [0, 0, 0],
                                                [0, 0, 0]],
                                               [[7, [561, 547], [576, 547]],
                                                [7, [561, 563], [576, 563]],
                                                [[546, 579], [561, 579], [576, 579]],
                                                [[546, 595], [561, 595], [576, 595]],
                                                [[546, 611], 7, [576, 611]],
                                                [[546, 627], 7, [576, 627]],
                                                [[546, 643], [561, 643], [576, 643]],
                                                [[546, 659], [561, 659], [576, 659]]])}

    def approval(self):
        elder = random.choice(list(self.elders_approval.keys()))
        self.elders_approval[elder] = True


class Player:
    def __init__(self):
        self.hit_points = 10
        self.search_range = 0
        self.attack_range = [5, 6]
        self.HP_Coordinates = [[272, 21], [287, 23], [303, 22], [315, 23], [327, 24], [342, 26], [355, 28],
                               [370, 30], [381, 30], [394, 26]]
        self.determination = 0
        self.determination_Coordinates = [[462, 26], [477, 26], [488, 26], [503, 26], [515, 26], [528, 26]]

    def increase_determination_pt(self):
        if self.determination < 6:
            self.determination += 1

    def increase_hp(self, n):
        hp = self.hit_points
        if hp + n < 10:
            self.hit_points = hp + n
        elif hp < 10:
            self.hit_points = 10


class Area:
    def __init__(self, area_name):
        self.area_name = area_name
        self.event = []
        self.tb_track = 0
        self.complete = False
        self.tb_HP = 6
        self.tb_attack_range = [1, 2, 3]
        self.tb_defeated = False

        self.grids_searched = 0
        self.searchBox = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]

        self.box_xy = {1: []}
        if self.area_name == "Coastal Caverns":
            self.beasts = {1: "Hooktooth Goblins", 2: "Shell-Cracker Troll", 3: "Land Shark",
                           4: "Nightmare Crab"}
            self.tb = "Dweller in the Tides"
            self.tb_hp_coordinates = [1183, 254]

            self.searchBox_coordinates = [[[39, 444], [56, 444], [73, 444], [39, 462], [56, 462], [73, 462]],
                                          [[103, 445], [121, 445], [136, 445], [103, 460], [121, 460], [136, 460]],
                                          [[95, 487], [112, 487], [127, 487], [95, 503], [112, 503], [127, 503]],
                                          [[64, 530], [81, 530], [95, 530], [64, 545], [81, 545], [95, 545]],
                                          [[129, 529], [144, 529], [160, 529], [129, 546], [144, 546], [160, 546]],
                                          [[137, 572], [152, 572], [168, 572], [137, 587], [152, 587], [168, 587]]]

        elif self.area_name == "Halebeard Peak":
            self.beasts = {1: "Frost Gremlin", 2: " Ice Bear", 3: "Blood Wolves", 4: "Horse Eater Hawk"}
            self.tb = "Giant of the Peaks"
            self.tb_hp_coordinates = [1349, 288]
            self.searchBox_coordinates = [[[403, 267], [418, 267], [434, 267], [403, 283], [418, 283], [434, 283]],
                                          [[361, 311], [379, 311], [395, 311], [361, 328], [379, 328], [395, 328]],
                                          [[432, 315], [448, 315], [464, 315], [432, 332], [448, 332], [464, 332]],
                                          [[494, 318], [508, 318], [523, 318], [494, 334], [508, 334], [523, 334]],
                                          [[554, 318], [571, 318], [587, 318], [554, 334], [571, 334], [587, 334]],
                                          [[572, 276], [587, 276], [602, 276], [572, 292], [587, 292], [602, 292]]]

        elif self.area_name == "The Scar":
            self.beasts = {1: "Hollow Birds", 2: " Spark Hounds", 3: "Coal Dragon", 4: "Ash Troll"}
            self.tb = "The Burning Man"
            self.tb_hp_coordinates = [995, 294]
            self.searchBox_coordinates = [[[255, 408], [270, 408], [285, 408], [255, 424], [270, 424], [285, 424]],
                                          [[316, 422], [334, 422], [350, 422], [316, 438], [334, 438], [350, 438]],
                                          [[387, 435], [396, 435], [412, 435], [387, 453], [396, 453], [412, 453]],
                                          [[444, 451], [458, 451], [471, 451], [444, 466], [458, 466], [471, 466]],
                                          [[506, 462], [522, 462], [537, 462], [506, 479], [522, 479], [537, 479]],
                                          [[568, 477], [584, 477], [599, 477], [568, 493], [584, 493], [599, 493]]]
