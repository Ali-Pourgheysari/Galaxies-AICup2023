import random

from src.game import Game

flag = False

LIMIT_OF_NODE = 8
DEFEND = False

ALL_MY_TROOPS_COUNT = 35

STATE_PUT_TROOPS = 1
STATE_ATTACK = 2
STATE_MOVE = 3
STATE_DEFENCIVE_TROOPS = 4


class Graph:
    def __init__(self, adj):
        # adj:  {0: [1, 2, 29, 24], 1: [0, 2, 3], 2: ...}
        self.graph_dict = adj


class GameInfo:
    STRATEGICAL_NODE = 1
    SIMPLE_NODE = 2

    STATE_PUT_TROOPS = 1
    STATE_ATTACK = 2
    STATE_MOVE = 3
    STATE_DEFENCIVE_TROOPS = 4

    def __init__(self, game: Game):
        self.game = game

        self.adj = {int(key): value for key, value in game.get_adj().items()}

        self.my_id = game.get_player_id()['player_id']

        self.all_nodes = {int(key): value for key, value in game.get_owners().items()}
        self.free_nodes = [node for node, owner in self.all_nodes.items() if owner == -1]
        self.enemy_nodes = [node for node, owner in self.all_nodes.items() if owner != self.my_id and owner != -1]

        self.strategical_nodes = game.get_strategic_nodes()['strategic_nodes']
        self.strategical_nodes_score = game.get_strategic_nodes()['score']
        self.dict_strategical_nodes_score = dict(zip(self.strategical_nodes, self.strategical_nodes_score))
        self.strategical_nodes_by_score = list(zip(self.strategical_nodes, self.strategical_nodes_score))
        self.strategical_nodes_by_score_sorted = [node for node, score in
                                                  sorted(self.strategical_nodes_by_score, key=lambda x: x[1],
                                                         reverse=True)]
        print(self.strategical_nodes, self.all_nodes)
        self.enemy_strategical_nodes = [node for node in self.strategical_nodes if
                                        self.all_nodes[node] != self.my_id and self.all_nodes[node] != -1]
        self.enemy_strategical_nodes_by_score_sorted = [node for node, owner in self.all_nodes.items() if
                                                        owner != self.my_id and owner != -1 and node in self.strategical_nodes and node in self.strategical_nodes_by_score_sorted]

        self.free_strategical_nodes = [node for node in self.strategical_nodes if self.all_nodes[node] == -1]
        self.free_strategical_nodes_by_score = [(node, score) for node, score in
                                                self.dict_strategical_nodes_score.items() if
                                                node in self.free_strategical_nodes]
        self.free_strategical_nodes_by_score_sorted = [node for node, score in
                                                       sorted(self.free_strategical_nodes_by_score, key=lambda x: x[1],
                                                              reverse=True)]
        self.my_strategical_nodes = [node for node in self.strategical_nodes if self.all_nodes[node] == self.my_id]
        self.my_simple_nodes = [node for node, owner in self.all_nodes.items() if owner == self.my_id and node not in
                                self.strategical_nodes]

        self.my_nodes = [node for node, owner in self.all_nodes.items() if owner == self.my_id]

        self.nodes_troops = {int(key): value for key, value in game.get_number_of_troops().items()}

        self.state = game.get_state()['state']

        self.enemy_strategical_nodes_next_to_my_node = []
        for node in self.enemy_strategical_nodes:
            neighbors = self.adj[node]
            have_my_node_neighbor = False
            for neighbor in neighbors:
                if neighbor in self.my_nodes:
                    have_my_node_neighbor = True
                    break
            if have_my_node_neighbor:
                self.enemy_strategical_nodes_next_to_my_node.append(node)

    def printer_number(self, number):
        n = ((number * 2) + 5 - 23) + 6.347
        # self.game.printer(str(n))
        return

    def printer_string(self, s):
        self.game.printer(s)
        return

    def get_reachable(self, node):
        return self.game.get_reachable(node)['reachable']

    def can_put_troops_limitation(self, troops_count, node_type):
        # todo check this
        # return troops_count < (ALL_MY_TROOPS_COUNT // len(self.my_nodes))
        return True

    def put_one_troop(self, node, message="Troop"):
        print("put troops get: ", node)
        print("put troops : ", self.game.put_one_troop(node), message)
        self.game.next_state()
        return

    def add_one_troops_to_nodes(self, node_id):
        self.nodes_troops[node_id] += 1

    def __str__(self):
        self.printer_number(LIMIT_OF_NODE)
        print("node limit", LIMIT_OF_NODE)
        print("my id: ", self.my_id)
        print("adj: ", self.adj)
        print("all nodes: ", self.all_nodes)
        print("free nodes: ", self.free_nodes)
        print("enemy nodes: ", self.enemy_nodes)
        print("strategical nodes: ", self.strategical_nodes)
        print("strategical nodes score: ", self.strategical_nodes_score)
        print("strategical nodes by score: ", self.strategical_nodes_by_score)
        print("strategical nodes by score sorted: ", self.strategical_nodes_by_score_sorted)
        print("enemy strategical nodes: ", self.enemy_strategical_nodes)
        print("enemy strategical nodes by score sorted: ", self.enemy_strategical_nodes_by_score_sorted)
        print("free strategical nodes: ", self.free_strategical_nodes)
        print("free strategical nodes by score: ", self.free_strategical_nodes_by_score)
        print("free strategical nodes by score sorted: ", self.free_strategical_nodes_by_score_sorted)
        print("my strategical nodes: ", self.my_strategical_nodes)
        print("my simple nodes: ", self.my_simple_nodes)
        print("my nodes: ", self.my_nodes)
        print("nodes troops: ", self.nodes_troops)
        return "my id: " + str(self.my_id)


def reinforce(game_info: GameInfo):
    # endangered my strategical node
    my_strategical_node_threat = dict()
    for strategical_node in game_info.my_strategical_nodes:
        neighbors = game_info.adj[strategical_node]
        strategical_node_troop = game_info.nodes_troops[strategical_node]
        for neighbor in neighbors:
            if neighbor not in game_info.my_nodes:
                enemy_nodes_troops = game_info.nodes_troops[neighbor]
                threat = enemy_nodes_troops - strategical_node_troop
                if strategical_node in my_strategical_node_threat.keys():
                    if threat > my_strategical_node_threat[strategical_node]:
                        my_strategical_node_threat[strategical_node] = threat
                else:
                    my_strategical_node_threat[strategical_node] = threat
    sort_my_strategical_node_threat = [x[0] for x in sorted(my_strategical_node_threat.items(),
                                                            key=lambda x: x[1],
                                                            reverse=True)]
    print('3')
    # check less than limitation of troops in my strategical node
    for node in sort_my_strategical_node_threat:
        if game_info.can_put_troops_limitation(game_info.nodes_troops[node], game_info.STRATEGICAL_NODE) and \
                my_strategical_node_threat[node] >= 0:
            # game_info.printer_string("r1")
            return node

    print('4')
    my_node_neighbors_to_my_strategical_node = set()
    for strategical_node in game_info.my_strategical_nodes:
        neighbors = game_info.adj[strategical_node]
        for neighbor in neighbors:
            if neighbor in game_info.my_nodes:
                my_node_neighbors_to_my_strategical_node.add(neighbor)
    my_node_neighbors_to_my_strategical_node = list()
    print('5')
    my_node_neighbors_to_my_strategical_node_threat = dict(my_node_neighbors_to_my_strategical_node)
    for node in my_node_neighbors_to_my_strategical_node:
        neighbors = game_info.adj[node]
        for neighbor in neighbors:
            if neighbor not in game_info.my_nodes:
                enemy_nodes_troops = game_info.nodes_troops[neighbor]
                if node in my_node_neighbors_to_my_strategical_node_threat.keys():
                    if enemy_nodes_troops > my_node_neighbors_to_my_strategical_node_threat[node]:
                        my_node_neighbors_to_my_strategical_node_threat[node] = enemy_nodes_troops
                else:
                    my_node_neighbors_to_my_strategical_node_threat[node] = enemy_nodes_troops

    sort_my_node_neighbors_to_my_strategical_node_threat = [x[0] for x in sorted(
        my_node_neighbors_to_my_strategical_node_threat.items(),
        key=lambda x: x[1],
        reverse=True)]
    print('6')
    for node in sort_my_node_neighbors_to_my_strategical_node_threat:
        if game_info.can_put_troops_limitation(game_info.nodes_troops[node], game_info.SIMPLE_NODE):
            # game_info.printer_string("r2")
            return node
    print('7')
    my_node_neighbors_to_enemy_strategical_node = set()
    for node in game_info.my_nodes:
        neighbors = game_info.adj[node]
        for neighbor in neighbors:
            if neighbor in game_info.enemy_strategical_nodes:
                my_node_neighbors_to_enemy_strategical_node.add(node)
    my_node_neighbors_to_enemy_strategical_node = list(my_node_neighbors_to_enemy_strategical_node)
    print('8')
    if my_node_neighbors_to_enemy_strategical_node:
        my_node_attack_to_enemy_troops = dict()
        for node in my_node_neighbors_to_enemy_strategical_node:
            neighbors = game_info.adj[node]
            for neighbor in neighbors:
                if neighbor in game_info.enemy_strategical_nodes:
                    if node in my_node_attack_to_enemy_troops.keys():
                        if game_info.nodes_troops[neighbor] < my_node_attack_to_enemy_troops[node]:
                            my_node_attack_to_enemy_troops[node] = game_info.nodes_troops[neighbor]
                    else:
                        my_node_attack_to_enemy_troops[node] = game_info.nodes_troops[neighbor]
        sort_my_node_attack_to_enemy_troops = [x[0] for x in sorted(my_node_attack_to_enemy_troops.items(),
                                                                    key=lambda x: x[1],
                                                                    reverse=False)]
        for node in sort_my_node_attack_to_enemy_troops:
            if game_info.can_put_troops_limitation(game_info.nodes_troops[node], game_info.SIMPLE_NODE):
                if game_info.nodes_troops[node] <= my_node_attack_to_enemy_troops[node]:
                    # game_info.printer_string("r3")
                    return node
    print('9')
    # reinforce without limitation
    all_my_nodes_threat = dict()
    for node in game_info.my_nodes:
        neighbors = game_info.adj[node]
        node_troop = game_info.nodes_troops[node]
        for neighbor in neighbors:
            if neighbor not in game_info.my_nodes:
                enemy_nodes_troops = game_info.nodes_troops[neighbor]
                threat = enemy_nodes_troops - node_troop
                if node in all_my_nodes_threat.keys():
                    if threat > all_my_nodes_threat[node]:
                        all_my_nodes_threat[node] = threat
                else:
                    all_my_nodes_threat[node] = threat
    sort_all_my_nodes_threat = [x[0] for x in sorted(all_my_nodes_threat.items(),
                                                     key=lambda x: x[1],
                                                     reverse=True)]
    print('sss3')
    # check less than limitation of troops in my strategical node
    for node in sort_all_my_nodes_threat:
        print("salam")
        if all_my_nodes_threat[node] >= 0:
            # game_info.printer_string("r4")
            return node

    my_node_by_troops = [node[0] for node in sorted([(node, troop) for node, troop in game_info.nodes_troops if node in game_info.my_nodes],
                               key=lambda x: x[1], reverse=False)]
    return my_node_by_troops[0]


def add_troop(game_info: GameInfo):
    print('add 1')
    ## place troop if game have free strategical node
    if game_info.free_strategical_nodes:
        return game_info.free_strategical_nodes_by_score_sorted[0]

    print('add 2')
    my_strategical_node_my_neighbors_count = dict()
    for strategical_node in game_info.my_strategical_nodes:
        my_strategical_node_my_neighbors_count[strategical_node] = 0
    for strategical_node in game_info.my_strategical_nodes:
        neighbors = game_info.adj[strategical_node]
        for neighbor in neighbors:
            if neighbor in game_info.my_nodes:
                if strategical_node in my_strategical_node_my_neighbors_count.keys():
                    my_strategical_node_my_neighbors_count[strategical_node] += 1

    my_strategical_node_my_neighbors_count_sorted = {node: neighbor for node, neighbor in
                                                     sorted(my_strategical_node_my_neighbors_count.items(),
                                                            key=lambda x: x[1], reverse=False)}

    count_minium = list(my_strategical_node_my_neighbors_count_sorted.values()).count(
        min(my_strategical_node_my_neighbors_count_sorted.values()))

    list_my_strategical_node_my_neighbors_count_sorted = list(
        my_strategical_node_my_neighbors_count_sorted.keys())
    if count_minium > 1:
        min_st = list_my_strategical_node_my_neighbors_count_sorted[:count_minium]
        st = list_my_strategical_node_my_neighbors_count_sorted[count_minium:]
        min_st_by_score = [(node, game_info.dict_strategical_nodes_score[node]) for node in min_st]
        min_st_by_score_sorted = [node for node, score in
                                  sorted(min_st_by_score, key=lambda x: x[1], reverse=True)]
        sorted_strategical_by_neighbors_score = min_st_by_score_sorted + st
        for node in sorted_strategical_by_neighbors_score:
            neighbors = game_info.adj[node]
            for neighbor in neighbors:
                if neighbor in game_info.free_nodes:
                    return neighbor
    else:
        print('add 3')
        for node in list_my_strategical_node_my_neighbors_count_sorted:
            neighbors = game_info.adj[node]
            for neighbor in neighbors:
                if neighbor in game_info.free_nodes:
                    return neighbor

    # if not game_info.enemy_strategical_nodes_next_to_my_node:
    #     for node in game_info.enemy_strategical_nodes_by_score_sorted:
    #         neighbors = game_info.adj[node]
    #         for neighbor in neighbors:
    #             if neighbor in game_info.free_nodes:
    #                 return neighbor
    #
    # elif game_info.enemy_strategical_nodes_next_to_my_node:
    #     neighbors = game_info.adj[game_info.enemy_strategical_nodes_next_to_my_node[0]]
    #     for neighbor in neighbors:
    #         if neighbor in game_info.free_nodes:
    #             return neighbor

    LIMIT_OF_NODE = len(game_info.my_nodes) - 1

    return None


def initial(game_info: GameInfo):
    print('00')
    # add troop
    if len(game_info.my_nodes) <= LIMIT_OF_NODE:
        node_id = add_troop(game_info)
        if node_id:
            game_info.put_one_troop(node_id, "add troop")
            return

    # reinforce
    node_id = reinforce(game_info)
    print(node_id)
    if node_id:
        game_info.put_one_troop(node_id, "reinforce")
        return
    return


def initializer(game: Game):
    print(game.get_player_id())

    # configure game info
    game_info = GameInfo(game)
    print(game_info)

    # initial(game_info)
    # return
    try:
        initial(game_info)
        return
    except:
        game.next_state()
        return


def get_my_troops_count_neighbours_of_enemy(game_info, node):
    neighbors = game_info.adj[node]
    troops_count = 0
    for neighbor in neighbors:
        troop = game_info.nodes_troops[neighbor]
        if neighbor in game_info.my_nodes:
            if troop > 1:
                troops_count += game_info.nodes_troops[neighbor]
    return troops_count


def can_attack(game_info, enemy_node):
    return get_my_troops_count_neighbours_of_enemy(game_info, enemy_node) > game_info.nodes_troops[enemy_node]


def get_fraction():
    return 0.1


def get_move_fraction():
    return 0.2


def attack(game: Game, game_info):
    attack_flag = False
    response = None

    enemy_neighbors_of_my_node = set()
    for node in game_info.my_nodes:
        print("1")
        neighbors = game_info.adj[node]
        for neighbor in neighbors:
            print("2")
            if neighbor in game_info.enemy_nodes:
                enemy_neighbors_of_my_node.add(neighbor)

    enemy_strategical_nodes = set()
    for enemy_node in enemy_neighbors_of_my_node:
        print("3")
        if enemy_node in game_info.strategical_nodes:
            enemy_strategical_nodes.add(enemy_node)
    enemy_strategical_nodes = list(enemy_strategical_nodes)
    enemy_strategical_nodes.sort(key=lambda x: get_my_troops_count_neighbours_of_enemy(game_info, x), reverse=True)

    for enemy_strategical_node in enemy_strategical_nodes:
        print("for attack ")
        while can_attack(game_info, enemy_strategical_node):
            print("attack attack ")
            neighbors = game_info.adj[enemy_strategical_node]
            neighbors = [x for x in neighbors if x in game_info.my_nodes]
            neighbors.sort(key=lambda x: game_info.nodes_troops[x], reverse=True)
            response = game.attack(neighbors[0], enemy_strategical_node, get_fraction(), get_move_fraction())
            attack_flag = True
            if response and response["won"]:
                return response
            elif response and "message" in response.keys() and response["message"] == "attack successful":
                game_info.nodes_troops = {int(key): value for key, value in game.get_number_of_troops().items()}

        if attack_flag:
            return response

    simple_nodes = set()
    for enemy_node in enemy_neighbors_of_my_node:
        print("4")
        if enemy_node not in game_info.strategical_nodes:
            simple_nodes.add(enemy_node)

    simple_nodes = list(simple_nodes)
    simple_nodes.sort(key=lambda x: get_my_troops_count_neighbours_of_enemy(game_info, x), reverse=True)

    for enemy_simple_node in simple_nodes:
        print("5")
        while can_attack(game_info, enemy_simple_node):
            print("6")
            neighbors = game_info.adj[enemy_simple_node]
            neighbors = [x for x in neighbors if x in game_info.my_nodes]
            neighbors.sort(key=lambda x: game_info.nodes_troops[x], reverse=True)
            response = game.attack(neighbors[0], enemy_simple_node, get_fraction(), get_move_fraction())
            print(response)
            if response and response["won"]:
                print(response)
                return response
            elif response and "message" in response.keys() and response["message"] == "attack successful":
                game_info.nodes_troops = {int(key): value for key, value in game.get_number_of_troops().items()}
            attack_flag = True
        if attack_flag:
            return response

    return response


def move(game: Game, game_info: GameInfo):
    # reinforce without limitation
    all_my_nodes_threat = dict()
    for node in game_info.my_nodes:
        neighbors = game_info.adj[node]
        node_troop = game_info.nodes_troops[node]
        for neighbor in neighbors:
            if neighbor not in game_info.my_nodes:
                enemy_nodes_troops = game_info.nodes_troops[neighbor]
                threat = enemy_nodes_troops - node_troop
                if node in all_my_nodes_threat.keys():
                    if threat > all_my_nodes_threat[node]:
                        all_my_nodes_threat[node] = threat
                else:
                    all_my_nodes_threat[node] = threat
    sort_all_my_nodes_threat = [x[0] for x in sorted(all_my_nodes_threat.items(),
                                                     key=lambda x: x[1],
                                                     reverse=True)]
    reverse_sort_all_my_nodes_threat = [x[0] for x in sorted(all_my_nodes_threat.items(),
                                                             key=lambda x: x[1],
                                                             reverse=False)]
    for node in sort_all_my_nodes_threat:
        reach = game_info.get_reachable(node)
        if all_my_nodes_threat[node] < 0:
            return
        for node_sos in reverse_sort_all_my_nodes_threat:
            if all_my_nodes_threat[node_sos] > 0:
                return
            if node_sos in reach:
                if abs(all_my_nodes_threat[node_sos]) > all_my_nodes_threat[node]:
                    game.move_troop(node_sos, node, abs(all_my_nodes_threat[node]))
                    return
                elif abs(all_my_nodes_threat[node_sos]) < all_my_nodes_threat[node]:
                    game.move_troop(node_sos, node, abs(all_my_nodes_threat[node_sos]))
                    return


def defend(game: Game, game_info: GameInfo):
    all_my_nodes_threat = dict()
    for node in game_info.my_strategical_nodes:
        neighbors = game_info.adj[node]
        node_troop = game_info.nodes_troops[node]
        for neighbor in neighbors:
            if neighbor not in game_info.my_nodes:
                enemy_nodes_troops = game_info.nodes_troops[neighbor]
                threat = enemy_nodes_troops - node_troop
                if node in all_my_nodes_threat.keys():
                    if threat > all_my_nodes_threat[node]:
                        all_my_nodes_threat[node] = threat
                else:
                    all_my_nodes_threat[node] = threat
    sort_all_my_nodes_threat = [x[0] for x in sorted(all_my_nodes_threat.items(),
                                                     key=lambda x: x[1],
                                                     reverse=True)]

    if all_my_nodes_threat[sort_all_my_nodes_threat[0]] > 0:
        game.fort(sort_all_my_nodes_threat[0], game_info.nodes_troops[sort_all_my_nodes_threat[0]] - 1)


def turn(game):
    global DEFEND
    game_info = GameInfo(game)

    # reinforce
    # todo we can not get new free node
    try:
        reinforce_faze2(game, game_info)
        game.next_state()
    except Exception as e:
        print(e)
        game.next_state()
    print("reinforce_ finish")

    # todo check condition for attack in different type of node
    print("attack start")
    game_info = GameInfo(game)
    try:
        for i in range(3):
            print("attack start2")
            attack(game, game_info)
            game_info = GameInfo(game)
        game.next_state()
    except:
        game.next_state()
    print("attack finish")

    try:
        game_info = GameInfo(game)
        move(game, game_info)
        game.next_state()
    except:
        game.next_state()

    try:
        if not DEFEND:
            game_info = GameInfo(game)
            defend(game, game_info)
            DEFEND = True
        game.next_state()
    except:
        game.next_state()


def reinforce_faze2(game: Game, game_info):
    node = add_troop(game_info)
    if node:
        game_info.add_one_troops_to_nodes(node)
        return node
    my_free_troops_count = game.get_number_of_troops_to_put()['number_of_troops']
    for i in range(my_free_troops_count):
        node_id = reinforce(game_info)
        print("node count trpps", node_id)
        game.put_troop(node_id, 1)
        if node_id:
            game_info.add_one_troops_to_nodes(node_id)
    return
