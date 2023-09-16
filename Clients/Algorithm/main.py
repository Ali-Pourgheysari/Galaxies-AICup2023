import random
from src.game import Game

flag = False

LIMIT_OF_NODE = 8
ALL_MY_TROOPS_COUNT = 35


class Graph:
    def __init__(self, adj):
        # adj:  {0: [1, 2, 29, 24], 1: [0, 2, 3], 2: ...}
        self.graph_dict = adj


class GameInfo:
    STRATEGICAL_NODE = 1
    SIMPLE_NODE = 2

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
        self.enemy_strategical_nodes = [node for node in self.strategical_nodes if self.all_nodes[node] != self.my_id]
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

    def can_put_troops_limitation(self, troops_count, node_type):
        return troops_count < (ALL_MY_TROOPS_COUNT // len(self.my_nodes))

    def put_one_troop(self, node, message="Troop"):
        print("put troops get: ", node)
        print("put troops : ", self.game.put_one_troop(node), message)

    def __str__(self):
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


def initializer(game: Game):
    print(game.get_player_id())

    # configure game info
    game_info = GameInfo(game)
    print(game_info)

    # initialize graph
    game_graph = Graph(game_info.adj)

    print('00')
    ## place troop if game have free strategical node
    if game_info.free_strategical_nodes:
        game_info.put_one_troop(game_info.free_strategical_nodes_by_score_sorted[0], "1")
        return

    print('11')
    if len(game_info.my_nodes) < LIMIT_OF_NODE and len(game_info.free_nodes):
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

        list_my_strategical_node_my_neighbors_count_sorted = list(my_strategical_node_my_neighbors_count_sorted.keys())
        if count_minium > 1:
            min_st = list_my_strategical_node_my_neighbors_count_sorted[:count_minium]
            st = list_my_strategical_node_my_neighbors_count_sorted[count_minium:]
            min_st_by_score = [(node, game_info.dict_strategical_nodes_score[node]) for node in min_st]
            min_st_by_score_sorted = [node for node, score in sorted(min_st_by_score, key=lambda x: x[1], reverse=True)]
            sorted_strategical_by_neighbors_score = min_st_by_score_sorted + st
            for node in sorted_strategical_by_neighbors_score:
                neighbors = game_info.adj[node]
                for neighbor in neighbors:
                    if neighbor in game_info.free_nodes:
                        game_info.put_one_troop(neighbor, "2")
                        return
        else:
            for node in list_my_strategical_node_my_neighbors_count_sorted:
                neighbors = game_info.adj[node]
                for neighbor in neighbors:
                    if neighbor in game_info.free_nodes:
                        game_info.put_one_troop(neighbor, "22")
                        return

        my_neighbors_of_my_node = dict()
        for node in game_info.my_nodes:
            print('22')
            neighbors = game_info.adj[node]
            free_neighbors = [neighbor for neighbor in neighbors if game_info.all_nodes[neighbor] == -1]

            for neighbor in free_neighbors:
                print('33')
                if neighbor in my_neighbors_of_my_node.keys():
                    my_neighbors_of_my_node[neighbor] += 1
                else:
                    my_neighbors_of_my_node[neighbor] = 1

        sort_my_neighbors_of_my_node = [x[0] for x in
                                        sorted(my_neighbors_of_my_node.items(), key=lambda x: x[1], reverse=True)]

        if len(sort_my_neighbors_of_my_node) > 1:
            for node in sort_my_neighbors_of_my_node:
                neighbors = game_info.adj[node]
                for neighbor in neighbors:
                    if neighbor in game_info.my_strategical_nodes:
                        game_info.put_one_troop(node, "2")
                        return

        elif len(sort_my_neighbors_of_my_node) == 1:
            game_info.put_one_troop(sort_my_neighbors_of_my_node[0], "3")
            return

        elif len(sort_my_neighbors_of_my_node) == 0:
            pass
            # strategical node
            # 1 check strategical node with one neighbor
            for strategical_node in game_info.free_strategical_nodes_by_score_sorted:
                print('66')
                if len(game_info.adj[strategical_node]) == 1:
                    game_info.put_one_troop(game_info.adj[strategical_node][0], "4")
                    return

            # 2 check neighbor of strategical node with one degree
            for strategical_node in game_info.free_strategical_nodes_by_score_sorted:
                print('77')
                neighbors = game_info.adj[strategical_node]
                for neighbor in neighbors:
                    print('88')
                    if len(game_info.adj[neighbor]) == 1:
                        game_info.put_one_troop(neighbor, "5")
                        return

            # 3 node connected to multiple strategical node
            # 4 node connected to one strategical node
            # 5 node connect to strategical node
            # 5.1 sort by troop
            # 5.2  sort by strategical node score
            node_to_strategical_node = dict()
            for free_node in game_info.free_nodes:
                print('99')
                neighbors = game_info.adj[free_node]
                strategical_neighbors = [neighbor for neighbor in neighbors if
                                         neighbor in game_info.free_strategical_nodes_by_score_sorted]
                if len(strategical_neighbors) >= 1:
                    node_to_strategical_node[free_node] = len(strategical_neighbors)
            if node_to_strategical_node:
                if max(node_to_strategical_node.values()) > 1:
                    sort_node_to_strategical_node = [x[0] for x in sorted(node_to_strategical_node.items(),
                                                                          key=lambda x: x[1],
                                                                          reverse=True)]

                else:
                    nodes_troops = game_info.nodes_troops
                    sort_node_to_strategical_node = [x[0] for x in sorted(node_to_strategical_node.items(),
                                                                          key=lambda x: nodes_troops[x[0]],
                                                                          reverse=False)]
                if sort_node_to_strategical_node:
                    game_info.put_one_troop(sort_node_to_strategical_node[0], "6")
                return

            # 6 select nearest node to strategical node

            for strategical_node in game_info.enemy_strategical_nodes_by_score_sorted:
                print('1010')
                neighbors = game_info.adj[strategical_node]
                for neighbor in neighbors:
                    if neighbor in game_info.free_nodes:
                        game_info.put_one_troop(neighbor, "7")
                        return
        game_info.put_one_troop(random.choice(game_info.free_nodes), "8 random choice")
        return

    print('2')
    # endangered my strategical node
    my_strategical_node_threat = dict()
    for strategical_node in game_info.my_strategical_nodes:
        neighbors = game_info.adj[strategical_node]
        for neighbor in neighbors:
            if neighbor not in game_info.my_nodes:
                enemy_nodes_troops = game_info.nodes_troops[neighbor]
                if strategical_node in my_strategical_node_threat.keys():
                    if enemy_nodes_troops > my_strategical_node_threat[strategical_node]:
                        my_strategical_node_threat[strategical_node] = enemy_nodes_troops
                else:
                    my_strategical_node_threat[strategical_node] = enemy_nodes_troops
    sort_my_strategical_node_threat = [x[0] for x in sorted(my_strategical_node_threat.items(),
                                                            key=lambda x: x[1],
                                                            reverse=True)]
    print('3')
    # check less than limitation of troops in my strategical node
    for node in sort_my_strategical_node_threat:
        if game_info.can_put_troops_limitation(game_info.nodes_troops[node], game_info.STRATEGICAL_NODE):
            game_info.put_one_troop(node, "8")
            return

    print('4')
    my_node_neighbors_to_my_strategical_node = list()
    for strategical_node in game_info.my_strategical_nodes:
        neighbors = game_info.adj[strategical_node]
        for neighbor in neighbors:
            if neighbor in game_info.my_nodes:
                my_node_neighbors_to_my_strategical_node.append(neighbor)
    print('5')
    my_node_neighbors_to_my_strategical_node_threat = dict()
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
            game_info.put_one_troop(node, "9")
            return
    print('7')
    my_node_neighbors_to_enemy_strategical_node = list()
    for node in game_info.my_nodes:
        neighbors = game_info.adj[node]
        for neighbor in neighbors:
            if neighbor in game_info.enemy_strategical_nodes:
                my_node_neighbors_to_enemy_strategical_node.append(node)
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
                                                                    reverse=True)]
        for node in sort_my_node_attack_to_enemy_troops:
            if game_info.can_put_troops_limitation(game_info.nodes_troops[node], game_info.SIMPLE_NODE):
                game_info.put_one_troop(node, "10")
                return
    print('9')
    # reinforce without limitation
    all_my_nodes_threat = dict()
    for node in game_info.my_nodes:
        neighbors = game_info.adj[node]
        for neighbor in neighbors:
            if neighbor not in game_info.my_nodes:
                enemy_nodes_troops = game_info.nodes_troops[neighbor]
                if node in all_my_nodes_threat.keys():
                    if enemy_nodes_troops > all_my_nodes_threat[node]:
                        all_my_nodes_threat[node] = enemy_nodes_troops
                else:
                    all_my_nodes_threat[node] = enemy_nodes_troops
    print('10')
    sort_all_my_nodes_threat = [x[0] for x in sorted(all_my_nodes_threat.items(),
                                                     key=lambda x: x[1],
                                                     reverse=True)]
    if sort_all_my_nodes_threat:
        game_info.put_one_troop(sort_all_my_nodes_threat[0], "11")
    return


def turn(game):
    global flag
    owner = game.get_owners()
    for i in owner.keys():
        if owner[str(i)] == -1 and game.get_number_of_troops_to_put()['number_of_troops'] > 1:
            print(game.put_troop(i, 1))

    list_of_my_nodes = []
    for i in owner.keys():
        if owner[str(i)] == game.get_player_id()['player_id']:
            list_of_my_nodes.append(i)
    print(game.put_troop(random.choice(list_of_my_nodes), game.get_number_of_troops_to_put()['number_of_troops']))
    print(game.get_number_of_troops_to_put())

    print(game.next_state())

    # find the node with the most troops that I own
    max_troops = 0
    max_node = -1
    owner = game.get_owners()
    for i in owner.keys():
        if owner[str(i)] == game.get_player_id()['player_id']:
            if game.get_number_of_troops()[i] > max_troops:
                max_troops = game.get_number_of_troops()[i]
                max_node = i
    # find a neighbor of that node that I don't own
    adj = game.get_adj()
    for i in adj[max_node]:
        if owner[str(i)] != game.get_player_id()['player_id'] and owner[str(i)] != -1:
            print(game.attack(max_node, i, 1, 0.5))
            break
    print(game.next_state())
    print(game.get_state())
    # get the node with the most troops that I own
    max_troops = 0
    max_node = -1
    owner = game.get_owners()
    for i in owner.keys():
        if owner[str(i)] == game.get_player_id()['player_id']:
            if game.get_number_of_troops()[i] > max_troops:
                max_troops = game.get_number_of_troops()[i]
                max_node = i
    print(game.get_reachable(max_node))
    x = game.get_reachable(max_node)['reachable']
    try:
        x.remove(int(max_node))
    except:
        print(x, max_node)
    destination = random.choice(x)
    print(game.move_troop(max_node, destination, 1))
    print(game.next_state())

    if flag == False:
        max_troops = 0
        max_node = -1
        owner = game.get_owners()
        for i in owner.keys():
            if owner[str(i)] == game.get_player_id()['player_id']:
                if game.get_number_of_troops()[i] > max_troops:
                    max_troops = game.get_number_of_troops()[i]
                    max_node = i

        print(game.get_number_of_troops()[str(max_node)])
        print(game.fort(max_node, 3))
        print(game.get_number_of_fort_troops())
        flag = True
    game.next_state()
