import pygame
import Game
import random

game = Game.UTBE()
player = game.Player()
village = game.Village()

bg = pygame.image.load("Board.png")
pygame.init()
window_width = 1542
window_height = 899
window = pygame.display.set_mode((window_width, window_height))
bg_image = pygame.image.load("Board.png")
running = True

window.blit(bg_image, (0, 0))


def getAction():
    action_list = ["search", "rest"]
    if True in village.towers_built.values():
        action_list.append("build")

    # print("Select one of the following actions by entering the corresponding number:")
    # for i in range(len(action_list)):
    #     print(str(i)+"-"+ action_list[i])
    return random.choice(action_list)


def calc_score(win, day):
    score = 0
    if game.Coastal_Caverns.tb_defeated:
        score += 50
    if game.The_Scar.tb_defeated:
        score += 50
    if game.Halebeard_Peak.tb_defeated:
        score += 50
    for i in village.towers_built.values():
        if i:
            score += 15
    if win:
        if village.huts == 0:
            score += 50
        score += 5 * (14 - day)
        score += 2 * player.hit_points
        score += (18 - village.doubt)
    print("Your score is " + str(score))


def death():
    print("You where killed.")
    calc_score(False, day)
    pygame.display.flip()
    input("Your strength evaporates and you slump to the ground in defeat. The shock of the final blow is, "
          "surprisingly, not what draws your focus. It is the relief you feel. For the first time in what must be "
          "years the tension in your back fades and a warm serenity washes over you as the world turns black"
          "\nPress any key to close.")
    pygame.quit()


def die():
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    if player.determination > 0:
        if random.choice([True, False]):
            check_box(player.determination_xy[player.determination], "0", "white")
            player.determination = -1
            die1 = random.randint(1, 6)
            die2 = random.randint(1, 6)
            print(" New role DP -1 ")

    return [die1, die2]


def select_area():
    a_name = []
    if not game.Coastal_Caverns.complete:
        a_name.append("Coastal Caverns")
    if not game.The_Scar.complete:
        a_name.append("The Scar")
    if not game.Halebeard_Peak.complete:
        a_name.append("Halebeard Peak")

    a = random.choice(a_name)  #int(input("Coastal Caverns-1 the Halebeard Peak-2, The Scar-3"))
    if a == "Coastal Caverns":
        area1 = game.Coastal_Caverns
    elif a == "Halebeard Peak":
        area1 = game.Halebeard_Peak
    else:
        area1 = game.The_Scar
    return area1


def search_area(area1):
    print("\nSearching " + area1.area_name)
    global encounter
    terrible_beast_hp = 6
    ar = [6]
    sr = []
    if "Sudden Clarity" in area1.event:
        ar.append(4)
        print("A flash of insight allows you to sense each beast’s weakness and know just how to avoid its "
              "attacks. Effect: +1 to your attack range in this region.")
    if "Madness" in area1.event:
        terrible_beast_hp += 2
        print("The beasts grow even more brazen and frenzied as the end of the world draws "
              "near. Effect: All beasts in this region have +2 HP")

    if "Foul Weather" in area1.event:
        sr1 = range(area1.grids_searched, area1.grids_searched + 2)
        print("Driving rain and fierce thunderstorms scour the landscape making traveling "
              "difficult. Effect: You only get two searches per day in this region.")
    else:
        sr1 = range(area1.grids_searched, area1.grids_searched + 3)  # search range

    for i in sr1:
        if i < 6:
            sr.append(i)

    for grid in sr:
        b = [0, 1, 2, 3, 4, 5]
        for lv in range(3):
            die1 = die()

            b1 = random.choice(b)  #Select box in grid
            b.remove(b1)
            b2 = random.choice(b)
            b.remove(b2)

            box1 = b1 - 1  # Agent selects next box in the grid
            box2 = b2 - 1
            area1.searchBox[grid][box1] = die1[0]
            coordinates2 = area1.searchBox_coordinates[grid][box1]

            check_box(coordinates2, str(die1[0]), "black")

            area1.searchBox[grid][box2] = die1[1]
            coordinates2 = area1.searchBox_coordinates[grid][box2]

            check_box(coordinates2, str(die1[1]), "black")
            print("Grid:\n " + str(area1.searchBox[grid][:3]) + "\n-" + str(area1.searchBox[grid][3:]) + "\nDie:" + str(
                die1))

        pygame.display.update()

        area1.grids_searched += 1
        if area1.grids_searched == 6:
            area1.complete = True

        result = area1.searchBox[grid][0] * 100 + area1.searchBox[grid][1] * 10 + area1.searchBox[grid][2] \
                 - area1.searchBox[grid][3] * 100 - area1.searchBox[grid][4] * 10 - area1.searchBox[grid][5]
        s_result = search_result(result)
        print("Result:" + str(result))

        if s_result == "Lair Found":
            print("\nLair Found " + area1.tb)
            print("DP++")
            player.determination += 1
            check_box(player.determination_xy[player.determination], "0", "blue")
            comat_tb(terrible_beast_hp,ar,area1)

        elif s_result == "Track Beast":
            print("\nTrack Beast")
            area1.tb_track += 1
            if area1.tb_track == 3:
                print("\nLair Found " + area1.tb)
                print("DP++")
                player.determination += 1
                check_box(player.determination_xy[player.determination], "0", "blue")
                player.increase_determination_pt()
                comat_tb(terrible_beast_hp, ar, area1)

        elif s_result == "Encounter":
            print("\nEncounter")
            beast_lv, ar, beast_ar, beast_h = encounter_chart(result)
            if "Madness" in area1.event:
                beast_h += 2
            if "Sudden Clarity" in area1.event:
                ar.append(4)
            for lv in area1.beasts.keys():
                if lv == beast_lv:
                    encounter = area1.beasts[lv]
            print("A " + encounter + " is attacking!")

            if combat(ar, beast_ar, beast_h):
                print("You have slayed the " + encounter + "\n")

        elif s_result == "Lair Found and Ambush!":
            print("\nLair Found and Ambush! " + area1.tb)
            print("DP++")
            player.determination += 1
            check_box(player.determination_xy[player.determination], "0", "blue")
            ar.append(5)
            comat_tb(terrible_beast_hp, ar, area1)



def comat_tb(terrible_beast_hp,ar,area1):
    terrible_beast_ar = [1, 2, 3]
    if combat(ar, terrible_beast_ar, terrible_beast_hp):
        check_box(area1.tb_hp_coordinates, "/////////////////////////////////", "red")
        area1.tb_defeated = True
        area1.complete = True
        village.approval()
        return True
    else:return False


def end_game(day):
    if game.Coastal_Caverns.tb_defeated and game.The_Scar.tb_defeated and game.Halebeard_Peak.tb_defeated:
        pygame.display.update()
        calc_score(True, day)
        print("You have defeated all three Terrible Beasts - Win")
        input("A calm wind carries the distant sound of brass horns as the Blazing Star Regiment begins its final "
              "approach. A solemn crowd gathers in the village square to watch the proceedings. You have proven "
              "your worth. The village elders nod to each other. There is a sense of nervousness and excitement "
              "in the crowd. Sipporos leads you into a nearby hut and closes the heavy door flap. In the darkness "
              "you hear the footsteps of armored soldiers outside the hut.")
        return True

    if game.time_track[day] == "D":
        calc_score(False, 14)
        print("You have run out of time - Loss")
        input("The sound of soldiers and horses fills the air as the Blazing Star Regiment assembles outside the "
              "village walls. A nervous crowd gathers in the village square to watch the proceedings. The elders "
              "consider you to have broken your promise. Furious that you have wasted their time and endangered "
              "the lives of the entire village, they cast you out of the village and into the waiting hands of "
              "the Blazing Star Regiment. Escape is impossible")
        return True
    return False

def add_doubt(n):
    village.doubt += n
    for d in range(village.doubt):
        if d < 18:
            check_box(village.xy_doubt[d], "X", "black")
    print("Doubt increased by "+str(n)+"\nThe Villagers’ Doubt: "+ str(village.doubt))
    if village.doubt >= 18:
        pygame.display.update()
        calc_score(False, day)
        print("You have lost the villagers’ trust")
        input("A crowd gathers in the village square. The knot in your stomach grows as you pick out the faces of "
              "your most vocal critics among the mob. Under a hail of stones you are chased out of the village "
              "into the unforgiving wilderness. You hear the thunder of hooves as a contingent of the Blazing "
              "Star Regiment races into the valley. Injured as you are, you realize escape is impossible.")
        return True
    else:return False

def search_result(result):
    if 1 <= result <= 10:
        return "Lair Found"
    elif 11 <= result <= 99:
        return "Track Beast"
    elif 100 <= result <= 555 or -555 <= result <= -1:
        return "Encounter"
    elif result == 0:
        return "Lair Found and Ambush!"


def select_tower():
    choice1 = []
    for key in village.towers_built.keys():
        if not village.towers_built[key]:
            choice1.append(key)

    tower_name = random.choice(choice1)  #Select Tower

    village.towers_built[tower_name] = True

    return tower_name


def attack_tower(tower2, coordinates1):
    for i in range(len(tower2)):
        for j in range(len(tower2[i])):
            if not (tower2[i][j] == 0 or tower2[i][j] == 7):
                tower2[i][j] = 0
                check_box(coordinates1[i][j], "X", "red")
                return tower2


def build(tn):
    t, coordanates = village.towers[tn]
    print(tn)
    while True:
        options = []
        d = die()
        d = d[0]
        if any(d in i for i in t):
            for r in range(len(t)):
                for c in range(len(t[r])):
                    if t[r][c] == d:
                        if not (c == (len(t[r]) - 1)):
                            if t[r][c + 1] == 0:
                                options.append([r, c + 1])
                        if not c == 0:
                            if t[r][c - 1] == 0:
                                options.append([r, c - 1])
                        if not r == 0:
                            if t[r - 1][c] == 0:
                                options.append([r - 1, c])
                        if not r == len(t) - 1:
                            if t[r + 1][c] == 0:
                                options.append([r + 1, c])

        else:
            print("New num")
            for r in range(len(t)):
                for c in range(len(t[r])):
                    if t[r][c] == 0:
                        available = True

                        if not (c == (len(t[r]) - 1)):
                            if not t[r][c + 1] in [0, 7]:
                                available = False
                        if not c == 0:
                            if not t[r][c - 1] in [0, 7]:
                                available = False
                        if not r == 0:
                            if not t[r - 1][c] in [0, 7]:
                                available = False
                        if not r == len(t) - 1:
                            if not t[r + 1][c] in [0, 7]:
                                available = False

                        if available:
                            options.append([r, c])

        if options == []:
            break

        tower_index = random.choice(options)  # AI would decide
        c = tower_index[1]
        r = tower_index[0]

        tower_coordinate = coordanates[r][c]
        check_box(tower_coordinate, str(d), "black")

        t[r][c] = d

        for i in t: print(i)
        print(str(d) + "---------------------")

    filled = True

    for r in range(len(t)):
        for c in range(len(t[r])):
            if t[r][c] == 0:
                tower_coordinate = coordanates[r][c]
                check_box(tower_coordinate, "X", "black")
                filled = False
    if filled:
        print("DP++")
        player.determination += 1
        check_box(player.determination_xy[player.determination], "0", "blue")

    return t, coordanates


def encounter_chart(roll):
    global attack_range, beast_attack_range, beast_hp
    encounter_lv = 0
    if (555 >= roll >= 500) or (-401 >= roll >= -555):
        encounter_lv = 4
    elif (499 >= roll >= 400) or (-301 >= roll >= -400):
        encounter_lv = 3
    elif (399 >= roll >= 300) or (-201 >= roll >= -300):
        encounter_lv = 2
    elif (299 >= roll >= 200) or (-101 >= roll >= -300):
        encounter_lv = 1
    elif (199 >= roll >= 100) or (-1 >= roll >= -100):
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
        attack_range = [5, 6]
        beast_attack_range = [1]
        beast_hp = 2
    elif encounter_lv == 2:
        attack_range = [5, 6]
        beast_attack_range = [1, 2]
        beast_hp = 2
    elif encounter_lv == 3:
        attack_range = [5, 6]
        beast_attack_range = [1, 2]
        beast_hp = 3
    elif encounter_lv == 4:
        attack_range = [6]
        beast_attack_range = [1, 2, 3]
        beast_hp = 3

    return encounter_lv, attack_range, beast_attack_range, beast_hp


def combat(attack_range, beast_attack_range, beast_hp):
    while (beast_hp > 0):
        die1 = die()
        if die1[0] == 6 and die1[1] == 6:
            print("CRITICAL HIT! +1 additional damage to beast")
            critical_hit = 1
            player.increase_determination_pt()
        else:
            critical_hit = 0
        for d in die1:
            if d in attack_range:
                print("attack beast")
                beast_hp -= 1 + critical_hit
            elif d in beast_attack_range:
                print("take damage")
                player.hit_points -= 1
                xy = player.HPcoordinates[player.hit_points]
                check_box(xy, "X", "black")
                if player.hit_points == 1:
                    print("DP++")
                    player.determination += 1
                    check_box(player.determination_xy[player.determination], "0", "blue")

        if player.hit_points <= 0:
            break

    if player.hit_points < 1:
        xy = player.HPcoordinates[player.hit_points]
        check_box(xy, "X", "black")
        death()
    else:
        print("Victory\nCurrent HP=" + str(player.hit_points))
        return True


def tb_attack(area2):
    # while area2.tb_defeated:  #terrible beast defeated
    #     area2 = select_area()
    global t_name
    if not area2.tb_defeated:
        if area2.area_name == "Coastal Caverns":
            t_name = "Eastern Tower"
        elif area2.area_name == "Halebeard Peak":
            t_name = "Southern Tower"
        elif area2.area_name == "The Scar":
            t_name = "South Western Tower"
        print("The " + area2.tb, " is attacking the " + t_name)
        if village.towers_built[t_name]:

            tower, coordinates = village.towers[t_name]
            die = random.randint(1, 6)
            if die == 2:
                village.towers[t_name] = attack_tower(tower, coordinates), coordinates
                print("The " + t_name + "took a hit!")
            elif die in [3, 4, 5]:
                for i in range(2):
                    village.towers[t_name] = attack_tower(tower, coordinates), coordinates
                print("The " + t_name + "took two hit's!")
            elif die == 6:
                for i in range(len(tower)):
                    for j in range(len(tower[i])):
                        if not tower[i][j] == 7:
                            tower[i][j] = 0
                            check_box(coordinates[i][j], "X", "white")
                print("The " + t_name + "was destroyed!")
                village.towers[t_name] = (tower, coordinates)
                village.towers_built[t_name] = False
            else:
                print("The " + t_name + "took no damage")

            for i in tower: print(i)
        else:
            print("A hut was destroyed!")
            for i in range(1, 9):
                not_destroyed, coordinates = village.huts[i]
                if not_destroyed:
                    check_box(coordinates, "X", "red")
                    village.huts[i] = (False, coordinates)
                    village.num_huts_destroyed += 1
                    add_doubt(2 * village.num_huts_destroyed)
                    break


def set_event():
    event_list = ["Sudden Clarity", "Foul Weather", "Madness"]
    for i in event_list:
        d = die()[0]
        if d in [1, 2]:
            game.Halebeard_Peak.event.append(i)
            if (i == "Madness") and "Foul Weather" in game.Halebeard_Peak.event and not game.Halebeard_Peak.tb_defeated:
                print("A region is affected by both Foul Weather and Madness at the same time, the Terrible Beast in "
                      "this region is overcome with rage and immediately descends into the valley to assault the "
                      "village.")
                tb_attack(game.Halebeard_Peak)
        elif d in [3, 4]:
            game.Coastal_Caverns.event.append(i)
            if (
                    i == "Madness") and "Foul Weather" in game.Coastal_Caverns.event and not game.Coastal_Caverns.tb_defeated:
                print("A region is affected by both Foul Weather and Madness at the same time, the Terrible Beast in "
                      "this region is overcome with rage and immediately descends into the valley to assault the "
                      "village.")
                tb_attack(game.Coastal_Caverns)
        elif d in [5, 6]:
            game.The_Scar.event.append(i)
            if (i == "Madness") and "Foul Weather" in game.The_Scar.event and not game.The_Scar.tb_defeated:
                print("A region is affected by both Foul Weather and Madness at the same time, the Terrible Beast in "
                      "this region is overcome with rage and immediately descends into the valley to assault the "
                      "village.")
                tb_attack(game.The_Scar)


def check_box(coordinates, value, colour):
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 15)
    txt = font.render(value, True, colour)
    window.blit(txt, (coordinates[0], coordinates[1]))
    pygame.display.update()


pygame.display.init()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     x, y = pygame.mouse.get_pos()
        #     print(f'Mouse clicked at {x}, {y}')
        #     check_box((x, y), "/////////////////////////////////", "red")
        #     pygame.display.update()

    for day in range(14):
        print("\n/////////////////////////////////////////////\nDAY:" + str(day + 1))
        check_box(game.time_track_xy[day], "X", "black")
        if game.time_track[day] == "!":
            area = select_area()
            while area.tb_defeated:
                area = select_area()
            tb_attack(area)

        game.reset_event()
        if game.time_track[day] == "E":
            set_event()

        action = getAction()  # SELECT ACTION
        print("Today you are going to " + action)

        if action == "search":
            area = select_area()
            search_area(area)
            if not area.tb_defeated:
                if add_doubt(1 + (village.num_huts_destroyed)):
                    input()
                    running = False
                    pygame.quit()
                    break

        elif action == "rest":
            add_doubt(1)
            if player.hit_points > 8:
                print("HP= 10")
                player.hit_points = 10
            else:
                print(2 * "HP++")
                for i in range(2):
                    check_box(player.HPcoordinates[player.hit_points + i], "X", "green")
                player.increase_hp(2)
                print("HP= " + str(player.hit_points))

        elif action == "build":
            tower_name = select_tower()
            village.towers[tower_name] = build(tower_name)
            if not (True in village.towers_built.values()):
                village.approval()

        pygame.display.update()
        if end_game(day):
            input()
            running = False
            pygame.quit()
            break

pygame.quit()
