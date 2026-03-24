import numpy as np
from .creature import Creature
from .neural_network import NeuralNetwork


class GeneticAlgorithm:
    def __init__(self, population_size=30, elitism=4, mutation_rate=0.05, mutation_strength=0.2):
        self.population_size = population_size
        self.elitism = elitism
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength

    def next_generation(self, creatures):
        preys = [c for c in creatures if not c.is_predator]
        preds = [c for c in creatures if c.is_predator]
        
        num_preds = self.population_size // 4
        num_preys = self.population_size - num_preds
        
        new_creatures = []
        
        # Helper to generate children for a specific sub-population
        def breed_subpop(sub_creatures, target_count):
            if not sub_creatures:
                return []
            sorted_c = sorted(sub_creatures, key=lambda c: c.get_fitness(), reverse=True)
            children = []
            
            # Elitism
            for i in range(min(self.elitism, len(sorted_c))):
                children.append(sorted_c[i].clone())
                
            # Fill with crossover
            while len(children) < target_count:
                pool = sorted_c[:max(1, self.elitism*2)]
                parent1 = np.random.choice(pool)
                parent2 = np.random.choice(pool)
                
                if np.random.rand() < 0.5:
                    child_brain = NeuralNetwork.crossover(parent1.brain, parent2.brain)
                else:
                    child_brain = NeuralNetwork()
                    child_brain.set_weights(parent1.brain.get_weights())
                    
                child_brain.mutate(self.mutation_rate, self.mutation_strength)
                child_size = max(0.5, parent1.size + np.random.uniform(-0.1, 0.1))
                child_vision = max(50.0, parent1.vision_range + np.random.uniform(-20, 20))
                child_fov = max(0.5, min(np.pi*2, parent1.fov + np.random.uniform(-0.5, 0.5)))
                
                child = Creature(np.random.uniform(0, 1), np.random.uniform(0, 1), 
                                 energy=100, brain=child_brain, 
                                 is_predator=parent1.is_predator, size=child_size,
                                 vision_range=child_vision, fov=child_fov)
                children.append(child)
                
            return children[:target_count]

        new_creatures.extend(breed_subpop(preys, num_preys))
        new_creatures.extend(breed_subpop(preds, num_preds))
        
        return new_creatures
