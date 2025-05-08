from itertools import permutations
from random import shuffle, randint

def is_hamiltonian_path(graph,path):
    for i in range(len(path) -1):
        if path[i+1] not in graph[path[i]]:
            return False
    return True

# stratą jest liczba błędnych (nieistniejących) krawędzi
def loss(graph,path):
    error = 0
    for i in range(len(path) -1):
        if path[i+1] not in graph[path[i]]:
            error += 1
    return error

def random_solution(graph):
    nodes = list(graph.keys())
    shuffle(nodes)
    return nodes

def generate_neighbours(path):
    neighbours = []
    for i in range(len(path)):
        for j in range(i+1, len(path)):
            neighbour = path.copy()
            neighbour[i],neighbour[j] = neighbour[j], neighbour[i]
            neighbours.append(neighbour)
    return neighbours


def Brute_force(graph):
    nodes = list(graph.keys())
    for perm in permutations(nodes):
        if is_hamiltonian_path(graph,perm):
            return perm
    return "Solution does not exist"

def hill_climbing(graph, max_iterations=1000):
    current = random_solution(graph)
    for i in range(max_iterations):
        neighbours = generate_neighbours(current)
        best = min(neighbours, key=lambda n: loss(graph,n))  # w liście neighbours dla każdego n obliczana jest strata
        if loss(graph,best) < loss(graph, current):
            current = best
        else:
            break
    return current, loss(graph,current)

def stochastic_hill_climbing(graph, max_iterations=1000):
    current = random_solution(graph)
    for i in range(max_iterations):
        neighbours = generate_neighbours(current)
        random = neighbours[randint(0,len(neighbours)-1)]
        if loss(graph,random) < loss(graph, current):
            current = random
    return current, loss(graph,current)


# Adjacency List
graph1 = {
    0: [1, 2],
    1: [0, 2, 3],
    2: [0, 1, 3],
    3: [1, 2, 4],
    4: [3]
}

graph2 = {
    0: [1, 3, 7],
    1: [0, 2, 6],
    2: [1, 3, 5],
    3: [0, 2, 4, 10],
    4: [3, 5, 9],
    5: [2, 4, 6, 8],
    6: [1, 5, 7],
    7: [0, 6, 8, 10],
    8: [5, 7, 9],
    9: [4, 8, 10],
    10: [3, 7, 9]
}


solution = Brute_force(graph2)
print("Exhaustive Search:", solution)

hc_solution, hc_loss = hill_climbing(graph2, 10000)
print("Hill Climbing:", hc_solution, "Loss:", hc_loss)

shc_solution, shc_loss = stochastic_hill_climbing(graph2, 10000)
print("Hill Climbing Stochastic:", shc_solution, "Loss:", shc_loss)

