import numpy as np
from .creature import Creature
from .neural_network import NeuralNetwork
from config import POPULATION_SIZE, ELITISM_COUNT, MUTATION_RATE, MUTATION_STRENGTH, STARTING_ENERGY


class GeneticAlgorithm:
    def __init__(self, population_size=POPULATION_SIZE, elitism=ELITISM_COUNT, mutation_rate=MUTATION_RATE, mutation_strength=MUTATION_STRENGTH):
        self.population_size = population_size
        self.elitism = elitism
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength

    def next_generation(self, creatures):
        if not creatures:
            return []
            
        sorted_c = sorted(creatures, key=lambda c: c.get_fitness(), reverse=True)
        children = []
        
        # Elitism
        for i in range(min(self.elitism, len(sorted_c))):
            children.append(sorted_c[i].clone())
            
        # Fill with crossover
        while len(children) < self.population_size:
            pool = sorted_c[:max(1, self.elitism*3)]
            parent1 = np.random.choice(pool)
            parent2 = np.random.choice(pool)
            
            if np.random.rand() < 0.5:
                child_brain = NeuralNetwork.crossover(parent1.brain, parent2.brain)
            else:
                child_brain = NeuralNetwork()
                child_brain.set_weights(parent1.brain.get_weights())
                
            child_brain.mutate(self.mutation_rate, self.mutation_strength)
            
            # Crossover and mutate traits
            child_size = max(0.5, (parent1.size + parent2.size)/2 + np.random.uniform(-0.1, 0.1))
            child_vision = max(50.0, (parent1.vision_range + parent2.vision_range)/2 + np.random.uniform(-20, 20))
            child_fov = max(0.5, min(np.pi, (parent1.fov + parent2.fov)/2 + np.random.uniform(-0.5, 0.5)))
            child_omnivore = max(0.0, min(1.0, (parent1.omnivore + parent2.omnivore)/2 + np.random.uniform(-0.1, 0.1)))
            
            child = Creature(np.random.uniform(0, 1), np.random.uniform(0, 1), 
                             energy=STARTING_ENERGY, brain=child_brain, 
                             size=child_size, vision_range=child_vision, fov=child_fov, omnivore=child_omnivore)
            children.append(child)
            
        return children[:self.population_size]
