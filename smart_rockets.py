
import math
import pygame
from numpy import array
from numpy import linalg
from numpy import random

# -------- Settings --------

WIDTH, HEIGHT = 640, 480
FPS = 60

population_size = 100
mutation_rate = 0.01
lifespan = 200
max_force = 0.1
max_speed = 4
elite_count = 1

# Colors
NAVY = (9, 12, 29)
ELITE_RED = (255, 50, 50)
ROCKET_GRAY = (180, 190, 205)
GREEN = (80, 210, 140)
LIGHT = (230, 230, 235)
GRAY = (100, 110, 130)

# Starting position
START_X = WIDTH // 2
START_Y = HEIGHT - 40

# Target and obstacle
target = array([WIDTH / 2, 60.0])
obstacle = pygame.Rect(220, 240, 200, 15)


# -------- DNA --------

class DNA:
    def __init__(self, length):
        self.genes = []

        for i in range(length):
            self.genes.append(self.randomForce())

    def randomForce(self):
        angle = random.uniform(0, 2 * math.pi)

        return array([
            math.cos(angle),
            math.sin(angle)
        ]) * max_force

    def crossover(self, partner):
        child = DNA(len(self.genes))
        midpoint = random.randint(len(self.genes) + 1)

        for i in range(len(self.genes)):
            if i < midpoint:
                child.genes[i] = self.genes[i].copy()
            else:
                child.genes[i] = partner.genes[i].copy()

        return child

    def mutate(self, mutationRate):
        for i in range(len(self.genes)):
            if random.random() < mutationRate:
                self.genes[i] = self.randomForce()


# -------- Rocket --------

class Rocket:
    def __init__(self, x, y, dna):
        self.dna = dna

        self.position = array([float(x), float(y)])
        self.velocity = array([0.0, 0.0])
        self.acceleration = array([0.0, 0.0])

        self.fitness = 0
        self.geneCounter = 0

        self.completed = False
        self.crashed = False
        self.isElite = False

    def applyForce(self, force):
        self.acceleration += force

    def update(self):
        if self.completed or self.crashed:
            return

        old_position = self.position.copy()

        self.velocity += self.acceleration

        # Limit velocity
        speed = linalg.norm(self.velocity)

        if speed > max_speed:
            self.velocity = self.velocity / speed * max_speed

        self.position += self.velocity
        self.acceleration *= 0

        # Check target collision
        distance = linalg.norm(self.position - target)

        if distance < 12:
            self.completed = True
            self.position = target.copy()
            return

        # Check boundaries
        if (
            self.position[0] < 0
            or self.position[0] > WIDTH
            or self.position[1] < 0
            or self.position[1] > HEIGHT
        ):
            self.crashed = True
            return

        # Check obstacle collision
        if obstacle.clipline(
            (float(old_position[0]), float(old_position[1])),
            (float(self.position[0]), float(self.position[1]))
        ):
            self.crashed = True

    def calculateFitness(self):
        distance = linalg.norm(self.position - target)

        self.fitness = 1 / (distance * distance + 1)

        # Bonus for reaching the target
        if self.completed:
            self.fitness *= 10

        # Penalty for crashing
        if self.crashed:
            self.fitness *= 0.1

    def run(self):
        if self.completed or self.crashed:
            return

        if self.geneCounter < len(self.dna.genes):
            self.applyForce(self.dna.genes[self.geneCounter])
            self.geneCounter += 1
            self.update()


# -------- Population --------

class Population:
    def __init__(self, mutation, populationSize, lifespan):
        self.mutationRate = mutation
        self.population = []
        self.generations = 0

        for i in range(populationSize):
            self.population.append(
                Rocket(START_X, START_Y, DNA(lifespan))
            )

    def fitness(self):
        for rocket in self.population:
            rocket.calculateFitness()

    def selection(self):
        total_fitness = sum(
            rocket.fitness for rocket in self.population
        )

        if total_fitness <= 0:
            probability = 1 / len(self.population)

            for rocket in self.population:
                rocket.fitness = probability

            return

        for rocket in self.population:
            rocket.fitness /= total_fitness

    def weightedSelection(self):
        index = 0
        start = random.random()

        while start > 0 and index < len(self.population):
            start -= self.population[index].fitness
            index += 1

        return self.population[max(0, index - 1)]

    def reproduction(self):
        new_population = []

        # Preserve the best rockets
        bestRockets = sorted(
            self.population,
            key=lambda rocket: rocket.fitness,
            reverse=True
        )

        for i in range(min(elite_count, len(bestRockets))):
            bestRocket = bestRockets[i]

            # Copy elite DNA without mutation
            eliteDNA = DNA(len(bestRocket.dna.genes))
            eliteDNA.genes = [
                gene.copy() for gene in bestRocket.dna.genes
            ]

            eliteRocket = Rocket(START_X, START_Y, eliteDNA)
            eliteRocket.isElite = True

            new_population.append(eliteRocket)

        # Create remaining rockets using crossover and mutation
        remaining = len(self.population) - len(new_population)

        for i in range(remaining):
            parentA = self.weightedSelection()
            parentB = self.weightedSelection()

            child = parentA.dna.crossover(parentB.dna)
            child.mutate(self.mutationRate)

            new_population.append(
                Rocket(START_X, START_Y, child)
            )

        self.population = new_population

    def live(self):
        for rocket in self.population:
            rocket.run()


# -------- Drawing --------

def draw_rocket(surface, rocket, size=7):
    vx, vy = rocket.velocity

    if vx or vy:
        angle = math.atan2(vy, vx)
    else:
        angle = -math.pi / 2

    points = [
        (size, 0),
        (-size * 0.6, size * 0.6),
        (-size * 0.6, -size * 0.6)
    ]

    ca = math.cos(angle)
    sa = math.sin(angle)

    px = float(rocket.position[0])
    py = float(rocket.position[1])

    polygon = [
        (
            px + x * ca - y * sa,
            py + x * sa + y * ca
        )
        for x, y in points
    ]

    # Elite rockets are always red
    if rocket.isElite:
        color = ELITE_RED
    elif rocket.completed:
        color = GREEN
    else:
        color = ROCKET_GRAY

    pygame.draw.polygon(surface, color, polygon)


# -------- Pygame Setup --------

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Rockets - Genetic Algorithm")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)

population = Population(
    mutation_rate,
    population_size,
    lifespan
)

frame = 0
running = True


# -------- Main Loop --------

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            target = array([
                float(event.pos[0]),
                float(event.pos[1])
            ])

    # Update rockets
    if frame < lifespan:
        population.live()
        frame += 1

    else:
        population.fitness()
        population.selection()
        population.reproduction()

        population.generations += 1
        frame = 0

    # Draw background
    screen.fill(NAVY)

    # Draw target
    pygame.draw.circle(
        screen,
        LIGHT,
        (int(target[0]), int(target[1])),
        12,
        2
    )

    # Draw obstacle
    pygame.draw.rect(
        screen,
        GRAY,
        obstacle
    )

    # Draw rockets
    for rocket in population.population:
        draw_rocket(screen, rocket)

    # Display generation
    generation_text = font.render(
        f"Generation: {population.generations}",
        True,
        LIGHT
    )

    screen.blit(generation_text, (10, 10))

    # Display lifespan
    lifespan_text = font.render(
        f"Frame: {frame}/{lifespan}",
        True,
        LIGHT
    )

    screen.blit(lifespan_text, (10, 40))

    # Display successful rockets
    completed = sum(
        rocket.completed for rocket in population.population
    )

    completed_text = font.render(
        f"Reached Target: {completed}/{population_size}",
        True,
        GREEN
    )

    screen.blit(completed_text, (10, 70))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
