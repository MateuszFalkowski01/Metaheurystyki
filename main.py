from itertools import permutations
from random import shuffle, randint, random, gauss
from math import exp
import csv


def load_graph(file):
    graph = {}
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            node = int(row[0])
            neighbours = list(map(int, row[1:]))
            graph[node] = neighbours
    return graph

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
        best = min(neighbours, key=lambda n: loss(graph,n))
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

def tabu_search(graph, max_iterations=1000, tabu_size=None):
    current = random_solution(graph)
    tabu_list = [current.copy()]
    best_solution = current.copy()
    best_loss = loss(graph,best_solution)
    checkpoint = []

    for i in range(max_iterations):
        neigbours = [n for n in generate_neighbours(current) if n not in tabu_list]

        if not neigbours:
            if checkpoint:
                current = checkpoint.pop()
                continue
            else:
                break

        best_neighbour = min(neigbours, key=lambda n: loss(graph,n))

        if loss(graph,best_neighbour) < best_loss:
            best_solution = best_neighbour.copy()
            best_loss = loss(graph,best_solution)
            checkpoint.append(current.copy())

        current = best_neighbour
        tabu_list.append(current.copy())
        if tabu_size is not None and len(tabu_list) > tabu_size:
            tabu_list.pop(0)

    return best_solution,best_loss

# otoczenie punktu roboczego - zbiór sąsiadów danego rozwiązania
# losowanie normalne faworyzuje sąsiadów bliższych aktualnego rozwiązania
def simulated_annealing(graph, max_iterations=1000, T0=100, alpha=0.95):
    current = random_solution(graph)
    current_loss = loss(graph,current)
    best = current.copy()
    best_loss = current_loss

    for i in range(max_iterations):
        T = T0 * (alpha ** i)
        if T <= 0:
            break

        neighbours = generate_neighbours(current)
        id = int(abs(gauss(0, 1)) % len(neighbours))
        neighbour = neighbours[id]
        neighbour_loss = loss(graph,neighbour)

        delta = neighbour_loss - current_loss

        if delta < 0 or random() < exp(-delta/T):
            current = neighbour
            current_loss = neighbour_loss
            if current_loss < best_loss:
                best = current
                best_loss = current_loss

    return best, best_loss


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

graph = load_graph("graph.csv")
solution = tabu_search(graph, 1000)
print("Tabu search:", solution)

solution, value = simulated_annealing(graph2, 10000)
print("Simulated Annealing:", solution, "Loss:", value)
