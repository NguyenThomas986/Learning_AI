
import random
import string

# Genetic Algorithm Settings
target = "i love hotdogs"
population_size = 100
mutation_rate = 0.01
max_generations = 1000

population = []
matingPool = []


def random_character():
    """Generate a random lowercase letter or space."""
    return random.choice(string.ascii_lowercase + " ")


class DNA:
    def __init__(self, length):
        self.genes = []
        self.fitness = 0

        for i in range(length):
            self.genes.append(random_character())

    def calc_fitness(self, target):
        score = 0

        for i in range(len(self.genes)):
            if self.genes[i] == target[i]:
                score += 1

        self.fitness = score / len(target)

    def crossover(self, partner):
        child = DNA(len(self.genes))
        midpoint = random.randrange(len(self.genes))

        for i in range(len(self.genes)):
            if i < midpoint:
                child.genes[i] = self.genes[i]
            else:
                child.genes[i] = partner.genes[i]

        return child

    def mutate(self, mutation_rate):
        for i in range(len(self.genes)):
            if random.random() < mutation_rate:
                self.genes[i] = random_character()


def setup():
    global population

    population = []

    for i in range(population_size):
        population.append(DNA(len(target)))


def selection():
    global matingPool
    matingPool = []

    for phrase in population:
        n = int(phrase.fitness * 100)

        for j in range(n):
            matingPool.append(phrase)


def reproduction():
    global population

    new_population = []

    for i in range(len(population)):
        parentA = random.choice(matingPool)
        parentB = random.choice(matingPool)

        child = parentA.crossover(parentB)
        child.mutate(mutation_rate)

        new_population.append(child)

    population = new_population


def draw():
    # Calculate fitness
    for phrase in population:
        phrase.calc_fitness(target)

    # Selection
    selection()

    # Reproduction
    if matingPool:
        reproduction()


# Run Genetic Algorithm
setup()
generation = 0

while generation < max_generations:
    # Evaluate current population
    for dna in population:
        dna.calc_fitness(target)

    # Find the best DNA
    best = max(population, key=lambda dna: dna.fitness)

    print(
        f"Generation {generation}: "
        f"{''.join(best.genes)} "
        f"Fitness: {best.fitness:.2%}"
    )

    # Check if target is reached
    if best.fitness == 1.0:
        print("Target found!")
        break

    # Generate next population
    draw()
    generation += 1

else:
    print("Maximum generations reached.")
