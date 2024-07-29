import random


class UTBE:
    def __init__(self):
        self.Coastal_Caverns = Area("Coastal Caverns")
        self.Halebeard_Peak = Area("Halebeard Peak")
        self.The_Scar = Area("The Scar")
        # self.turn = 0
        self.time_track = ["E", " ", "!", "E", " ", "!", "E", " ", "!", "E", " ", "!", "E", "D"]
        self.time_track_xy = [[602, 41], [583, 41], [583, 57], [583, 76], [602, 85], [621, 86], [621, 103], [602, 107],
                              [583, 119], [602, 129], [621, 138], [621, 157], [602, 164], [583, 167]]
        #self.tb_defeated = {"Giant of the Peaks": False, "Dweller in the Tides": False, "The Burning Man": False}

    def reset_event(self):
        self.Coastal_averns.event = []
        self.The_Scar.event = []
        self.Halebeard_Peak.event = []


    class Player:
        def __init__(self):
            self.hit_points = 10
            self.HPcoordinates = [[272, 21], [287, 23], [303, 22], [315, 23], [327, 24], [342, 26], [355, 28],
                                  [370, 30], [381, 30], [394, 26]]

            self.determination = 0
            self.determination_xy = [[462,26],[477,26],[488,26],[503,26],[515,26],[528,26]]

        def increase_determination_pt(self):
            if self.determination < 6:
                self.determination += 1

        def increase_hp(self, n):
            hp = self.hit_points
            if hp + n < 10:
                self.hit_points = hp + n
            elif hp < 10:
                self.hit_points = 10

    class Village:
        def __init__(self):
            self.num_huts_destroyed =0
            self.huts = {1: (True, [256, 711]), 2: (True, [301, 724]), 3: (True, [337, 748]), 4: (True, [290, 760]),
                         5: (True, [248, 746]), 6: (True, [417, 639]), 7: (True, [452, 655]), 8: (True, [483, 672]),
                         9: (True, [545, 699])}
            self.doubt = 0
            self.xy_doubt =[[224,99],[235,95],[247,87],[259,82],[272,79],[284,73],[233,108],[246,101],[257,97],[269,91],[281,87],[294,82],[242,119],[256,114],[268,106],[279,102],[291,95],[304,92]]
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
            elders =[]
            for k in self.elders_approval.keys():elders.append(k)
            elder = random.choice(elders)
            self.elders_approval[elder] = True

class Area:
    def __init__(self, area_name):
        self.area_name = area_name
        self.event = []
        self.tb_track = 0
        self.complete = False
        self.tb_defeated = False

        self.grids_searched = 0
        self.searchBox = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        self.box_xy = {1: []}
        if self.area_name == "Coastal Caverns":
            self.beasts = {1: "Hooktooth Goblins", 2: "Shell-Cracker Troll", 3: "Land Shark",
                           4: "Nightmare Crab"}
            self.tb = "Dweller in the Tides"
            self.tb_hp_coordinates = [1183,254]

            self.searchBox_coordinates = [[[39, 444], [56, 444], [73, 444], [39, 462], [56, 462], [73, 462]],
                                          [[103, 445], [121, 445], [136, 445], [103, 460], [121, 460], [136, 460]],
                                          [[95, 487], [112, 487], [127, 487], [95, 503], [112, 503], [127, 503]],
                                          [[64, 530], [81, 530], [95, 530], [64, 545], [81, 545], [95, 545]],
                                          [[129, 529], [144, 529], [160, 529], [129, 546], [144, 546], [160, 546]],
                                          [[137, 572], [152, 572], [168, 572], [137, 587], [152, 587], [168, 587]]]

        elif self.area_name == "Halebeard Peak":
            self.beasts = {1: "Frost Gremlin", 2: " Ice Bear", 3: "Blood Wolves", 4: "Horse Eater Hawk"}
            self.tb = "Giant of the Peaks"
            self.tb_hp_coordinates = [1349,288]
            self.searchBox_coordinates = [[[403, 267], [418, 267], [434, 267], [403, 283], [418, 283], [434, 283]],
                                          [[361, 311], [379, 311], [395, 311], [361, 328], [379, 328], [395, 328]],
                                          [[432, 315], [448, 315], [464, 315], [432, 332], [448, 332], [464, 332]],
                                          [[494, 318], [508, 318], [523, 318], [494, 334], [508, 334], [523, 334]],
                                          [[554, 318], [571, 318], [587, 318], [554, 334], [571, 334], [587, 334]],
                                          [[572, 276], [587, 276], [602, 276], [572, 292], [587, 292], [602, 292]]]

        elif self.area_name == "The Scar":
            self.beasts = {1: "Hollow Birds", 2: " Spark Hounds", 3: "Coal Dragon", 4: "Ash Troll"}
            self.tb = "The Burning Man"
            self.tb_hp_coordinates = [995,294]
            self.searchBox_coordinates = [[[255, 408], [270, 408], [285, 408], [255, 424], [270, 424], [285, 424]],
                                          [[316, 422], [334, 422], [350, 422], [316, 438], [334, 438], [350, 438]],
                                          [[387, 435], [396, 435], [412, 435], [387, 453], [396, 453], [412, 453]],
                                          [[444, 451], [458, 451], [471, 451], [444, 466], [458, 466], [471, 466]],
                                          [[506, 462], [522, 462], [537, 462], [506, 479], [522, 479], [537, 479]],
                                          [[568, 477], [584, 477], [599, 477], [568, 493], [584, 493], [599, 493]]]
