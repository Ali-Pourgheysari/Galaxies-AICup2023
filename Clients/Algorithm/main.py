import random
from src.game import Game

flag = False

LIMIT_OF_NODE = 7
ALL_MY_TROOPS_COUNT = 35


class Graph:
    # get list of edge with node id like this and initialize graph : [[1,2],[2,3],[3,4]]
    def __init__(self, edges):
        self.edges = edges
        self.graph_dict = {}
        for start, end in self.edges:
            if start in self.graph_dict.keys():
                self.graph_dict[start].append(end)
            else:
                self.graph_dict[start] = [end]

    def get_shortest_path(self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if start not in self.graph_dict.keys():
            return None
        shortest_path = None
        for node in self.graph_dict[start]:
            if node not in path:
                new_path = self.get_shortest_path(node, end, path)
                if new_path:
                    if shortest_path is None or len(new_path) < len(shortest_path):
                        shortest_path = new_path

        return shortest_path


class GameInfo:
    STRATEGICAL_NODE = 1
    SIMPLE_NODE = 2

    def __init__(self, game: Game):
        self.game = game

        self.adj = game.get_adj()

        self.my_id = game.get_player_id()['player_id']

        self.all_nodes = game.get_owners()
        self.free_nodes = [node for node, owner in self.all_nodes.items if owner == -1]
        self.enemy_nodes = [node for node, owner in self.all_nodes.items if owner != self.my_id and owner != -1]

        self.strategical_nodes = game.get_strategic_nodes()['strategic_nodes']
        self.strategical_nodes_score = game.get_strategic_nodes()['score']
        self.strategical_nodes_by_score = list(zip(self.strategical_nodes, self.strategical_nodes_score))
        self.strategical_nodes_by_score_sorted = [node for node, score in
                                                  sorted(self.strategical_nodes_by_score, key=lambda x: x[1],
                                                         reverse=True)]
        self.enemy_strategical_nodes = [node for node, owner in self.all_nodes.items if
                                        owner != self.my_id and owner != -1 and node in self.strategical_nodes]
        self.enemy_strategical_nodes_by_score_sorted = [node for node, owner in self.all_nodes.items if
                                                        owner != self.my_id and owner != -1 and node in self.strategical_nodes and node in self.strategical_nodes_by_score_sorted]

        self.free_strategical_nodes = [node for node in self.all_nodes.keys() if node == -1]
        self.free_strategical_nodes_by_score = list(zip(self.free_strategical_nodes, self.strategical_nodes_score))
        self.free_strategical_nodes_by_score_sorted = [node for node, score in
                                                       sorted(self.free_strategical_nodes_by_score, key=lambda x: x[1],
                                                              reverse=True)]
        self.my_strategical_nodes = [node for node in self.all_nodes.keys() if node == self.my_id]
        self.my_simple_nodes = [node for node, owner in self.all_nodes.items if owner == self.my_id and node not in
                                self.strategical_nodes]

        self.my_nodes = [node for node, owner in self.all_nodes.items if owner == self.my_id]

        self.nodes_troops = game.get_number_of_troops()

    def can_put_troops_limitation(self, troops_count, node_type):
        return troops_count < (ALL_MY_TROOPS_COUNT // len(self.my_nodes))


def initializer(game: Game):
    # configure game info
    game_info = GameInfo(game)

    # initialize graph
    game_graph = Graph(game_info.adj)

    ## place troop if game have free strategical node
    if game_info.free_strategical_nodes:
        game.put_one_troop(game_info.free_strategical_nodes_by_score_sorted[0])
        return

    ##
    if len(game_info.my_nodes) < LIMIT_OF_NODE and len(game_info.free_nodes):
        my_neighbors_of_my_node = dict()
        for node in game_info.my_nodes:

            neighbors = game_info.adj[node]
            free_neighbors = [neighbor for neighbor in neighbors if game_info.all_nodes[neighbor] == -1]

            for neighbor in free_neighbors:
                if neighbor in my_neighbors_of_my_node.keys():
                    my_neighbors_of_my_node[neighbor] += 1
                else:
                    my_neighbors_of_my_node[neighbor] = 1

        sort_my_neighbors_of_my_node = [x[0] for x in
                                        sorted(my_neighbors_of_my_node.items(), key=lambda x: x[1], reverse=True)]

        if len(sort_my_neighbors_of_my_node) > 1:
            node_to_nearest_strategical_node = dict()
            for node in sort_my_neighbors_of_my_node:
                for my_strategical_node in game_info.my_strategical_nodes:
                    shortest_path = game_graph.get_shortest_path(node, my_strategical_node)
                    if shortest_path:
                        if node in node_to_nearest_strategical_node.keys():
                            if len(shortest_path) < node_to_nearest_strategical_node[node]:
                                node_to_nearest_strategical_node[node] = len(shortest_path)
                        else:
                            node_to_nearest_strategical_node[node] = len(shortest_path)
            sort_node_to_nearest_strategical_node = [x[0] for x in
                                                     sorted(node_to_nearest_strategical_node.items(),
                                                            key=lambda x: x[1],
                                                            reverse=False)]
            game.put_one_troop(sort_node_to_nearest_strategical_node[0])
            return

        elif len(sort_my_neighbors_of_my_node) == 1:
            game.put_one_troop(sort_my_neighbors_of_my_node[0])
            return

        elif len(sort_my_neighbors_of_my_node) == 0:
            pass
            # strategical node
            # 1 check strategical node with one neighbor
            for strategical_node in game_info.free_strategical_nodes_by_score_sorted:
                if len(game_info.adj[strategical_node]) == 1:
                    game.put_one_troop(game_info.adj[strategical_node][0])
                    return


            # 2 check neighbor of strategical node with one degree
            for strategical_node in game_info.free_strategical_nodes_by_score_sorted:
                neighbors = game_info.adj[strategical_node]
                for neighbor in neighbors:
                    if len(game_info.adj[neighbor]) == 1:
                        game.put_one_troop(neighbor)
                        return

            # 3 node connected to multiple strategical node
            # 4 node connected to one strategical node
            # 5 node connect to strategical node
            # 5.1 sort by troop
            # 5.2  sort by strategical node score
            node_to_strategical_node = dict()
            for free_node in game_info.free_nodes:
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
                game.put_one_troop(sort_node_to_strategical_node[0])
                return

            # 6 select nearest node to strategical node
            free_node_to_strategical_node_path = dict()
            for free_node in game_info.free_nodes:
                for strategical_node in game_info.enemy_strategical_nodes_by_score_sorted:
                    shortest_path = game_graph.get_shortest_path(free_node, strategical_node)
                    if shortest_path:
                        if free_node in free_node_to_strategical_node_path.keys():
                            if len(shortest_path) < free_node_to_strategical_node_path[free_node]:
                                free_node_to_strategical_node_path[free_node] = len(shortest_path)
                        else:
                            free_node_to_strategical_node_path[free_node] = len(shortest_path)
            sort_free_node_to_strategical_node_path = [x[0] for x in sorted(free_node_to_strategical_node_path.items(),
                                                                            key=lambda x: x[1],
                                                                            reverse=False)]
            game.put_one_troop(sort_free_node_to_strategical_node_path[0])
            return

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
    # check less than limitation of troops in my strategical node
    for node in sort_my_strategical_node_threat:
        if game_info.can_put_troops_limitation(game_info.nodes_troops[node], game_info.STRATEGICAL_NODE):
            game.put_one_troop(node)
            return

    my_node_neighbors_to_my_strategical_node = list()
    for strategical_node in game_info.my_strategical_nodes:
        neighbors = game_info.adj(strategical_node)
        for neighbor in neighbors:
            if neighbor in game_info.my_nodes:
                my_node_neighbors_to_my_strategical_node.append(neighbor)

    my_node_neighbors_to_my_strategical_node_threat = dict()
    for node in my_node_neighbors_to_my_strategical_node:
        neighbors = game_info.adj(node)
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

    for node in sort_my_node_neighbors_to_my_strategical_node_threat:
        if game_info.can_put_troops_limitation(game_info.nodes_troops[node], game_info.SIMPLE_NODE):
            game.put_one_troop(node)
            return

    my_node_neighbors_to_enemy_strategical_node = list()
    for node in game_info.my_nodes:
        neighbors = game_info.adj(node)
        for neighbor in neighbors:
            if neighbor in game_info.enemy_strategical_nodes:
                my_node_neighbors_to_enemy_strategical_node.append(node)

    if my_node_neighbors_to_enemy_strategical_node:
        my_node_attack_to_enemy_troops = dict()
        for node in my_node_neighbors_to_enemy_strategical_node:
            neighbors = game_info.adj(node)
            for neighbor in neighbors:
                if neighbor in game_info.enemy_strategical_nodes:
                    if node in my_node_attack_to_enemy_troops.keys():
                        if game_info.nodes_troops(neighbor) < my_node_attack_to_enemy_troops[node]:
                            my_node_attack_to_enemy_troops[node] = game_info.nodes_troops(neighbor)
                    else:
                        my_node_attack_to_enemy_troops[node] = game_info.nodes_troops(neighbor)
        sort_my_node_attack_to_enemy_troops = [x[0] for x in sorted(my_node_attack_to_enemy_troops.items(),
                                                                    key=lambda x: x[1],
                                                                    reverse=True)]
        for node in sort_my_node_attack_to_enemy_troops:
            if game_info.can_put_troops_limitation(game_info.nodes_troops[node], game_info.SIMPLE_NODE):
                game.put_one_troop(node)
                return

    # reinforce without limitation
    all_my_nodes_threat = dict()
    for node in game_info.my_nodes:
        neighbors = game_info.adj(node)
        for neighbor in neighbors:
            if neighbor not in game_info.my_nodes:
                enemy_nodes_troops = game_info.nodes_troops[neighbor]
                if node in all_my_nodes_threat.keys():
                    if enemy_nodes_troops > all_my_nodes_threat[node]:
                        all_my_nodes_threat[node] = enemy_nodes_troops
                else:
                    all_my_nodes_threat[node] = enemy_nodes_troops

    sort_all_my_nodes_threat = [x[0] for x in sorted(all_my_nodes_threat.items(),
                                                            key=lambda x: x[1],
                                                            reverse=True)]
    game.put_one_troop(sort_all_my_nodes_threat[0])
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
