import numpy as np
from .neural_network import NeuralNetwork
from config import STARTING_ENERGY, PREY_ENERGY_YIELD, DEFAULT_VISION_RANGE, BASE_SPEED_MULTIPLIER, EXPLORATION_FITNESS_WEIGHT, EFFICIENCY_FITNESS_WEIGHT


class Creature:
    def __init__(self, x, y, energy=STARTING_ENERGY, brain=None, size=1.0, vision_range=DEFAULT_VISION_RANGE, fov=np.pi, omnivore=0.5):
        self.x = x
        self.y = y
        self.energy = energy
        self.alive = True
        self.food_eaten = 0
        self.total_energy_gained = 0.0
        self.survival_time = 0
        self.bonus_fitness = 0
        self.age = 0
        self.size = size
        self.vision_range = vision_range
        self.fov = fov
        self.shout_intensity = 0.0
        self.mating_urge = 0.0
        self.mating_cooldown = 0
        self.omnivore = omnivore
        self.angle = np.random.uniform(0, 2 * np.pi)
        self.distance_traveled = 0.0
        self.brain = brain if brain else NeuralNetwork()

    def update(self, food_list, other_creatures, width, height, is_winter=False, hearing_level=0.0):
        if not self.alive:
            return
        inputs = np.zeros(26)
        inputs[24] = self.energy / STARTING_ENERGY
        inputs[25] = hearing_level
        
        if self.fov >= np.pi * 2 - 0.01:
            ray_angles = np.linspace(0, 2 * np.pi, 8, endpoint=False) + self.angle
        else:
            ray_angles = np.linspace(-self.fov/2, self.fov/2, 8) + self.angle
            
        ray_length = self.vision_range
        
        if self.mating_cooldown > 0:
            self.mating_cooldown -= 1
            
        for i, angle in enumerate(ray_angles):
            ray_dx = np.cos(angle)
            ray_dy = np.sin(angle)
            
            best_f_dist = ray_length
            best_c_dist = ray_length
            best_c_omni = 0.0
            
            for food in food_list:
                dx = food.x - self.x
                dy = food.y - self.y
                dist_sq = dx**2 + dy**2
                if dist_sq == 0 or dist_sq > ray_length**2: continue
                dist = np.sqrt(dist_sq)
                if (dx/dist)*ray_dx + (dy/dist)*ray_dy > 0.95 and dist < best_f_dist:
                    best_f_dist = dist
                    
            for c in other_creatures:
                dx = c.x - self.x
                dy = c.y - self.y
                dist_sq = dx**2 + dy**2
                if dist_sq == 0 or dist_sq > ray_length**2: continue
                dist = np.sqrt(dist_sq)
                if (dx/dist)*ray_dx + (dy/dist)*ray_dy > 0.95 and dist < best_c_dist:
                    best_c_dist = dist
                    best_c_omni = c.omnivore
            
            if best_f_dist < ray_length: inputs[i] = 1.0 - (best_f_dist / ray_length)
            if best_c_dist < ray_length: 
                inputs[8 + i] = 1.0 - (best_c_dist / ray_length)
                inputs[16 + i] = best_c_omni
        
        outputs = self.brain.forward(inputs)
        
        self.angle += outputs[0] * 0.15
        # Herbivores are leaner and faster — up to +40% speed for omnivore=0
        speed_bonus = 1.0 + 0.4 * (1.0 - self.omnivore)
        speed = max(0, outputs[1]) * (BASE_SPEED_MULTIPLIER / np.sqrt(self.size)) * speed_bonus
        self.shout_intensity = max(0.0, min(1.0, outputs[2]))
        self.mating_urge = max(0.0, min(1.0, outputs[3]))
        
        self.x += np.cos(self.angle) * speed
        self.y += np.sin(self.angle) * speed
        self.distance_traveled += speed
        
        # Wrap around window
        self.x = self.x % width
        self.y = self.y % height
        
        # Energy drain: herbivores (omnivore=0) cost 40% less to run
        metabolic_factor = 0.6 + 0.4 * self.omnivore
        base_drain = (0.15 * self.size + (0.0001 * self.age) + (self.vision_range / 3000.0) + (self.fov / 50.0) + (self.shout_intensity * 0.02)) * metabolic_factor
        # Herbivores are cold-adapted: only ×1.2 winter drain vs ×1.5 for carnivores
        if is_winter:
            winter_mult = 1.2 + 0.3 * self.omnivore
            base_drain *= winter_mult
            
        self.energy -= base_drain
        self.survival_time += 1
        self.age += 1
        if self.energy <= 0:
            self.alive = False

    def check_eat(self, food_list, other_creatures, food_radius=6):
        creature_radius = 10 * np.sqrt(self.size)
        
        # Eat other creatures logic
        for c in other_creatures:
            if not c.alive: continue
            
            can_eat = False
            # Standard Predation: must be more carnivorous AND large enough (90% size)
            if self.omnivore > c.omnivore + 0.2:
                if self.size >= c.size * 0.9:
                    can_eat = True
            
            # Cannibalism: high-omnivore carnivores can eat other carnivores if they are much larger (>30%)
            elif self.omnivore > 0.7 and c.omnivore > 0.7:
                if self.size > c.size * 1.3:
                    can_eat = True
            
            if can_eat:
                c_rad = 10 * np.sqrt(c.size)
                dist_sq = (self.x - c.x)**2 + (self.y - c.y)**2
                if dist_sq < (creature_radius + c_rad)**2:
                    c.alive = False
                    gain = PREY_ENERGY_YIELD * self.omnivore
                    self.energy += gain
                    self.total_energy_gained += gain
                    self.food_eaten += 1
                    
        # Eat food items based on type
        for i, food in enumerate(food_list):
            dist_sq = (self.x - food.x) ** 2 + (self.y - food.y) ** 2
            if dist_sq < (creature_radius + food_radius) ** 2:
                if food.type == "grass":
                    gain = food.current_energy * (1.0 - self.omnivore)
                elif food.type == "berry":
                    gain = food.current_energy * (1.0 - self.omnivore * 0.4)
                elif food.type == "meat":
                    gain = food.current_energy * self.omnivore
                else:
                    gain = 0.0
                # Only consume if it's actually worth eating (> 5 energy)
                if gain > 5.0:
                    self.energy += gain
                    self.total_energy_gained += gain
                    self.food_eaten += 1
                    return i
                
        return None

    def get_fitness(self):
        distance_bonus = self.distance_traveled * EXPLORATION_FITNESS_WEIGHT
        # Efficiency is now based on energy gained per unit of survival time
        efficiency_bonus = (self.total_energy_gained / (self.survival_time + 1)) * EFFICIENCY_FITNESS_WEIGHT
        # Fitness = survival + (energy gained) + child bonus + distance bonus + efficiency
        return self.survival_time + self.total_energy_gained + self.bonus_fitness + distance_bonus + efficiency_bonus

    def clone(self):
        clone = Creature(self.x, self.y, energy=STARTING_ENERGY, 
                         size=self.size, vision_range=self.vision_range, fov=self.fov, omnivore=self.omnivore)
        clone.brain.set_weights(self.brain.get_weights())
        return clone
