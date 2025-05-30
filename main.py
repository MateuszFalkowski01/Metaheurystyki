from itertools import permutations
from random import shuffle, randint, random, sample
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
        if loss(graph,perm) == 0:
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
def simulated_annealing(graph, max_iterations=1000, T0=200, alpha=0.95):
    current = random_solution(graph)
    current_loss = loss(graph,current)
    best = current.copy()
    best_loss = current_loss

    for i in range(max_iterations):
        T = T0 * (alpha ** i)
        if T <= 0:
            break

        neighbours = generate_neighbours(current)
        id = randint(0,len(neighbours) -1)
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

# Krzyżowanie jednopunktowe - losujemy punkt krzyżowania, a następnie kopiujemy rodzica 1 do punktu i dopełniamy elementami z rodzica 2
def one_point_corssover(parent1,parent2):
    size = len(parent1)
    point = randint(1, size - 2)
    child1 = parent1[:point] + [x for x in parent2 if x not in parent1[:point]]
    child2 = parent2[:point] + [x for x in parent1 if x not in parent2[:point]]
    return child1, child2

# Krzyżowanie pozycyjne - losujemy pozycje połowy pozycji z rodzica 1 i wypełniamy elementami z rodzica 2
def crossover_position(parent1,parent2):
    size = len(parent1)
    positions = sample(range(size), size // 2)

    child1 = [-1] * size
    for i in positions:
        child1[i] = parent1[i]
    fill = [x for x in parent2 if x not in child1]
    for i in range(size):
        if child1[i] == -1:
            child1[i] = fill.pop(0)

    child2 = [-1] * size
    for i in positions:
        child2[i] = parent2[i]
    fill = [x for x in parent1 if x not in child2]
    for i in range(size):
        if child2[i] == -1:
            child2[i] = fill.pop(0)
    return child1, child2

# zamiana dwóch losowych genów
def mutation_swap(id, mutation_rate=0.05):
    if random() < mutation_rate:
        i,j = randint(0, len(id) - 1), randint(0, len(id) - 1)
        id[i], id[j] = id[j], id[i]
    return id

# odwrócenie losowego fragmentu
def mutation_inversion(id, mutation_rate=0.05):
    if random() < mutation_rate:
        i,j = sorted([randint(0, len(id) - 1), randint(0, len(id) - 1)])
        id[i:j+1] = reversed(id[i:j+1])
    return id

def stop_by_iterations(iteration, max_iterations, **kwargs):
    return iteration >= max_iterations

def stop_by_stagnation(iteration, max_iterations, stagnation_counter, max_stagnation):
    return iteration >= max_iterations or stagnation_counter >= max_stagnation

def tournament(population, graph, k=5):
    participants = sample(population, k)
    participants.sort(key=lambda i: loss(graph, i))
    return participants[0]

def genetic_algorithm(graph,
                      population_size=100,
                      max_iterations=1000,
                      crossover_method="one_point",
                      mutation_method="swap",
                      stop_condition="iterations",
                      elite_size=2,
                      max_stagnation=100):

    population = [random_solution(graph) for i in range(population_size)]
    population.sort(key=lambda x: loss(graph, x))
    best = population[0]
    best_loss = loss(graph, best)
    iteration = 0
    stagnation_counter = 0

    crossover_fun = one_point_corssover if crossover_method == "one_point" else crossover_position
    mutation_fun = mutation_swap if mutation_method == "swap" else mutation_inversion
    stop_fun = stop_by_iterations if stop_condition == "iterations" else stop_by_stagnation

    while not stop_fun(iteration=iteration,max_iterations=max_iterations, stagnation_counter=stagnation_counter, max_stagnation=max_stagnation):
        new_population = population[:elite_size]


        while len(new_population) < population_size:
            p1 = tournament(population, graph)
            p2 = tournament(population, graph)
            child1, child2 = crossover_fun(p1,p2)
            child1 = mutation_fun(child1)
            child2 = mutation_fun(child2)
            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)

        population = sorted(new_population, key=lambda i: loss(graph, i))
        current_best = population[0]
        current_loss = loss(graph, current_best)

        if current_loss < best_loss:
            best = current_best
            best_loss = current_loss
            stagnation_counter = 0
        else:
            stagnation_counter += 1

        iteration += 1

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
print("Brute force:", solution)

hc_solution, hc_loss = hill_climbing(graph2, 10000)
print("Hill Climbing:", hc_solution, "Loss:", hc_loss)

shc_solution, shc_loss = stochastic_hill_climbing(graph2, 10000)
print("Hill Climbing Stochastic:", shc_solution, "Loss:", shc_loss)

graph = load_graph("graph.csv")
solution, tabu_loss = tabu_search(graph, 1000)
print("Tabu search:", solution, "Loss:", tabu_loss)

solution, value = simulated_annealing(graph2, 10000)
print("Simulated Annealing:", solution, "Loss:", value)

solution, gen_loss = genetic_algorithm(graph2, 100, 1000, "one_point", "swap", "iterations", 2, 200)
print("Genetic Algorithm:", solution, "Loss:", gen_loss)
