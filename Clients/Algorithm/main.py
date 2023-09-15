import random
from src.game import Game
import time

flag = False

LIMIT_OF_NODE = 7


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


def initializer(game: Game):
    # all nodes with neighbors
    adj = game.get_adj()

    # initialize graph
    game_graph = Graph(adj)

    # get my id
    my_id = game.get_player_id()['player_id']

    # get strategic nodes and scores
    strategic_nodes = game.get_strategic_nodes()['strategic_nodes']
    strategic_nodes_score = game.get_strategic_nodes()['score']

    # get all node with owner
    all_node = game.get_owners()

    # get all my node
    my_nodes = [node for node, owner in all_node.items if owner == my_id]

    # get all node with number of troops
    nodes_troops = game.get_number_of_troops()

    # get free node
    free_node = [node for node, owner in all_node.items if node == -1]

    # get free strategical node
    free_strategical_node = [node for node in free_node if node in strategic_nodes]

    # get my strategical node
    my_strategical_nodes = [node for node in my_nodes if node in strategic_nodes]

    ## place troop if game have free strategical node
    if free_strategical_node:
        free_strategical_node.sort(key=lambda x: x[1], reverse=True)
        game.put_one_troop(free_strategical_node[0])

    ##
    if len(my_nodes) < LIMIT_OF_NODE and len(free_node):
        my_neighbors_of_my_node = dict()
        for node in my_nodes:

            neighbors = adj[node]
            neighbors = [neighbor for neighbor in neighbors if all_node[neighbor] == -1]

            for neighbor in neighbors:
                if neighbor in my_neighbors_of_my_node.keys():
                    my_neighbors_of_my_node[neighbor] += 1
                else:
                    my_neighbors_of_my_node[neighbor] = 1

        sort_my_neighbors_of_my_node = [x[0] for x in
                                        sorted(my_neighbors_of_my_node.items(), key=lambda x: x[1], reverse=True)]

        if len(sort_my_neighbors_of_my_node) > 1:
            node_to_nearest_strategical_node = dict()
            for node in sort_my_neighbors_of_my_node:
                for my_strategical_node in my_strategical_nodes:
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
                                                            reverse=True)]
            game.put_one_troop(sort_node_to_nearest_strategical_node[0])

        elif len(sort_my_neighbors_of_my_node) == 1:
            game.put_one_troop(sort_my_neighbors_of_my_node[0])

        elif len(sort_my_neighbors_of_my_node) == 0:
            pass
            # strategical node
            # 1 check strategical node with one neighbor
            # 2 check neighbor of strategical node with one degree
            # 3 node connected to multiple strategical node
            # 4 node connected to one strategical node
            # 5 node connect to strategical node
            # 5.1 sort by troop
            # 5.2  sort by strategical node score
            # 6 select nearest node to strategical node

    # endangered strategical node
    my_strategical_node = [node for node, owner in all_node.items if node in strategic_nodes and owner == my_id]

    for node in my_strategical_node:
        node_troops
        node_neighbors = adj[node]
        enemy_neighbors = [neighbor for neighbor in node_neighbors if all_node[neighbor] != my_id]

    # strategic_nodes = list(zip(strategic_nodes, score))
    # strategic_nodes.sort(key=lambda x: x[1], reverse=True)
    # strategic_nodes, score = list(zip(*strategic_nodes))
    #
    # # print(game.get_turn_number())
    # owner = game.get_owners()
    # for i in strategic_nodes:
    #     if owner[str(i)] == -1:
    #         print(game.put_one_troop(i), "-- putting one troop on", i)
    #         return
    # adj = game.get_adj()
    # for i in strategic_nodes:
    #     for j in adj[str(i)]:
    #         if owner[str(j)] == -1:
    #             print(game.put_one_troop(j), "-- putting one troop on neighbor of strategic node", j)
    #             return
    # my_id = game.get_player_id()['player_id']
    # nodes = []
    # nodes.extend([i for i in strategic_nodes if owner[str(i)] == my_id])
    # for i in strategic_nodes:
    #     for j in adj[str(i)]:
    #         if owner[str(j)] == my_id:
    #             nodes.append(j)
    # nodes = list(set(nodes))
    # node = random.choice(nodes)
    # game.put_one_troop(node)
    # print("3-  putting one troop on", node)


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
