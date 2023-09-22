import random

from src.game import Game

flag = False

LIMIT_OF_NODE = 7
ALL_MY_TROOPS_COUNT = 35
SIMPLE_NODE_TO_STRATEGICAL_NODE = dict()
INIT_SIMPLE_NODE_TO_STRATEGICAL_NODE = False
SIMPLE_NODE_COUNT = 2


class Graph:
    def __init__(self, adj):
        # adj:  {0: [1, 2, 29, 24], 1: [0, 2, 3], 2: ...}
        self.graph_dict = adj


class GameInfo:
    STRATEGICAL_NODE = 1
    SIMPLE_NODE = 2

    def __init__(self, game: Game):
        global INIT_SIMPLE_NODE_TO_STRATEGICAL_NODE, SIMPLE_NODE_TO_STRATEGICAL_NODE
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
        self.simple_nodes = [node for node, owner in self.all_nodes.items() if node not in
                             self.strategical_nodes]

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

        if not INIT_SIMPLE_NODE_TO_STRATEGICAL_NODE:
            SIMPLE_NODE_TO_STRATEGICAL_NODE = self.get_simple_node_to_strategical_node()
            INIT_SIMPLE_NODE_TO_STRATEGICAL_NODE = True

        self.simple_node_to_strategical_node = SIMPLE_NODE_TO_STRATEGICAL_NODE

    def get_simple_node_to_strategical_node(self):
        result = dict()
        for node in self.simple_nodes:
            for strategical_node in self.strategical_nodes:
                path = self.shortest_path(node, strategical_node)
                if path:
                    if node in result.keys():
                        if len(path) < len(result[node]):
                            result[node] = (strategical_node, len(path))
                    else:
                        result[node] = (strategical_node, len(path))
        return result

    def shortest_path(self, start, end):
        visited = {start}
        queue = [[start]]
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == end:
                return path
            for adjacent in self.adj.get(node, []):
                if adjacent not in visited:
                    visited.add(adjacent)
                    queue.append(path + [adjacent])

    def can_put_troops_limitation(self, troops_count, node_type):
        return troops_count < (ALL_MY_TROOPS_COUNT // len(self.my_nodes))

    def put_one_troop(self, node, message="Troop"):
        print("put troops get: ", node)
        print("put troops : ", self.game.put_one_troop(node), message)
        self.game.next_state()

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

    print('place troop if game have free strategical node')
    ## place troop if game have free strategical node
    if game_info.free_strategical_nodes:
        game_info.put_one_troop(game_info.free_strategical_nodes_by_score_sorted[0],
                                "place troop if game have free strategical node")
        return

    ## place troop to nearest free node to strategical node
    print('place troop to nearest free node to strategical node')
    if game_info.free_nodes and len(game_info.my_simple_nodes) < SIMPLE_NODE_COUNT:
        sort_my_simple_free_nodes_nearest_to_strategical_nodes = [node[0] for node in sorted(
            {node: value for node, value in game_info.simple_node_to_strategical_node.items() if
             node in game_info.free_nodes}.items(), key=lambda x: x[1][1])]
        game_info.put_one_troop(sort_my_simple_free_nodes_nearest_to_strategical_nodes[0],
                                "place troop to nearest free node to strategical node")
        return

    ## place troop in endanger strategical node
    print('place troop in endanger strategical node')
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

    # check less than limitation of troops in my strategical node
    print('check less than limitation of troops in my strategical node')
    for node in sort_my_strategical_node_threat:
        if game_info.can_put_troops_limitation(game_info.nodes_troops[node], game_info.STRATEGICAL_NODE) and \
                my_strategical_node_threat[node] >= 0:
            game_info.put_one_troop(node, "check less than limitation of troops in my strategical node")
            return

    ## place troop in my simple node for attack
    print('place troop in my simple node for attack')
    my_simple_node_threat = dict()
    for simple_node in game_info.my_simple_nodes:
        neighbors = game_info.adj[simple_node]
        simple_node_troop = game_info.nodes_troops[simple_node]
        for neighbor in neighbors:
            if neighbor not in game_info.my_nodes:
                enemy_nodes_troops = game_info.nodes_troops[neighbor]
                threat = enemy_nodes_troops - simple_node_troop
                if simple_node in my_simple_node_threat.keys():
                    if threat > my_simple_node_threat[simple_node]:
                        my_simple_node_threat[simple_node] = threat
                else:
                    my_simple_node_threat[simple_node] = threat
    sort_my_simple_node_threat = [x[0] for x in sorted(my_simple_node_threat.items(),
                                                       key=lambda x: x[1],
                                                       reverse=True)]

    # check less than limitation of troops in my simple node
    print('check less than limitation of troops in my simple node')
    for node in sort_my_simple_node_threat:
        if sort_my_simple_node_threat[node] >= 0:
            game_info.put_one_troop(node, "check less than limitation of troops in my simple node")
            return

    game_info.game.next_state()
    return


def turn(game):

