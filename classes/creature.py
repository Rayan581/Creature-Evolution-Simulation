import numpy as np
from .neural_network import NeuralNetwork


class Creature:
    def __init__(self, x, y, energy=100, brain=None, is_predator=False, size=1.0, vision_range=150.0, fov=np.pi*2):
        self.x = x
        self.y = y
        self.energy = energy
        self.alive = True
        self.food_eaten = 0
        self.survival_time = 0
        self.bonus_fitness = 0
        self.age = 0
        self.size = size
        self.vision_range = vision_range
        self.fov = fov
        self.shout_intensity = 0.0
        self.mating_urge = 0.0
        self.mating_cooldown = 0
        self.angle = np.random.uniform(0, 2 * np.pi)
        self.is_predator = is_predator
        self.brain = brain if brain else NeuralNetwork()

    def update(self, food_list, prey_list, predator_list, width, height, is_winter=False, hearing_level=0.0):
        if not self.alive:
            return
        inputs = np.zeros(26)
        inputs[24] = self.energy / 100.0
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
            
            def check_ray(targets, is_creature_list=False):
                closest = ray_length
                for t in targets:
                    tx = t.x if is_creature_list else t[0]
                    ty = t.y if is_creature_list else t[1]
                    dx = tx - self.x
                    dy = ty - self.y
                    dist_sq = dx**2 + dy**2
                    if dist_sq == 0 or dist_sq > ray_length**2: continue
                    dist = np.sqrt(dist_sq)
                    if (dx/dist)*ray_dx + (dy/dist)*ray_dy > 0.95 and dist < closest:
                        closest = dist
                return closest

            f_dist = check_ray(food_list, False)
            p_dist = check_ray(prey_list, True)
            pd_dist = check_ray(predator_list, True)
            
            if f_dist < ray_length: inputs[i] = 1.0 - (f_dist / ray_length)
            if p_dist < ray_length: inputs[8 + i] = 1.0 - (p_dist / ray_length)
            if pd_dist < ray_length: inputs[16 + i] = 1.0 - (pd_dist / ray_length)
        
        outputs = self.brain.forward(inputs)
        
        self.angle += outputs[0] * 0.15
        speed = max(0, outputs[1]) * (3.5 / np.sqrt(self.size))
        self.shout_intensity = max(0.0, min(1.0, outputs[2]))
        self.mating_urge = max(0.0, min(1.0, outputs[3]))
        
        self.x += np.cos(self.angle) * speed
        self.y += np.sin(self.angle) * speed
        # Wrap around window
        self.x = self.x % width
        self.y = self.y % height
        
        # Energy drain scales with size, age, vision range, fov and shout
        base_drain = 0.3 * self.size + (0.0005 * self.age) + (self.vision_range / 1000.0) + (self.fov / 20.0) + (self.shout_intensity * 0.05)
        if is_winter:
            base_drain *= 2.0
            
        self.energy -= base_drain
        self.survival_time += 1
        self.age += 1
        if self.energy <= 0:
            self.alive = False

    def check_eat(self, food_list, prey_list, food_radius=6):
        creature_radius = 10 * np.sqrt(self.size)
        if self.is_predator:
            for p in prey_list:
                dist_sq = (self.x - p.x)**2 + (self.y - p.y)**2
                p_radius = 10 * np.sqrt(p.size)
                if dist_sq < (creature_radius + p_radius)**2:
                    p.alive = False
                    self.energy += 50
                    self.food_eaten += 1
                    return None
            return None
        else:
            for i, (fx, fy) in enumerate(food_list):
                dist_sq = (self.x - fx) ** 2 + (self.y - fy) ** 2
                if dist_sq < (creature_radius + food_radius) ** 2:
                    self.energy += 30
                    self.food_eaten += 1
                    return i  # Index of food eaten
            return None

    def get_fitness(self):
        return self.survival_time + self.food_eaten * 50 + self.bonus_fitness

    def clone(self):
        clone = Creature(self.x, self.y, energy=100, is_predator=self.is_predator, 
                         size=self.size, vision_range=self.vision_range, fov=self.fov)
        clone.brain.set_weights(self.brain.get_weights())
        return clone
