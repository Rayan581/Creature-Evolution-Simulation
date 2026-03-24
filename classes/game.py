from classes.brain_io import save_brain, load_brain
import pygame
from config import *

import numpy as np
import random
from classes.creature import Creature
from classes.genetic_algorithm import GeneticAlgorithm
from classes.neural_network import NeuralNetwork


class Game:
    def __init__(self):
        self.energy_preview_creature = None
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        # Simulation parameters
        self.population_size = 32
        self.food_count = 20
        self.best_prey_file = "best_prey_brain.pkl"
        self.best_predator_file = "best_predator_brain.pkl"
        
        self.best_prey_weights = load_brain(self.best_prey_file)
        if self.best_prey_weights is not None and self.best_prey_weights[0].shape[0] != 26:
            self.best_prey_weights = None
            
        self.best_pred_weights = load_brain(self.best_predator_file)
        if self.best_pred_weights is not None and self.best_pred_weights[0].shape[0] != 26:
            self.best_pred_weights = None
            
        self.creatures = []
        num_preds = self.population_size // 4
        
        spawned_preds = 0
        spawned_prey = 0
        
        for i in range(self.population_size):
            is_predator = (i < num_preds)
            c = Creature(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), is_predator=is_predator)
            
            if is_predator and self.best_pred_weights is not None and spawned_preds < 3:
                c.brain.set_weights(self.best_pred_weights)
                c.brain.mutate(mutation_rate=0.1, mutation_strength=0.3)
                spawned_preds += 1
            elif not is_predator and self.best_prey_weights is not None and spawned_prey < 7:
                c.brain.set_weights(self.best_prey_weights)
                c.brain.mutate(mutation_rate=0.1, mutation_strength=0.3)
                spawned_prey += 1
                
            self.creatures.append(c)
        self.food = [self.spawn_food() for _ in range(self.food_count)]
        self.ga = GeneticAlgorithm(population_size=self.population_size)
        self.generation = 1
        self.season_timer = 0
        self.is_winter = False
        self.graph_data_prey = []
        self.graph_data_pred = []
        self.graph_timer = 0
        self.prev_champion = None  # Track top performer from previous gen
        self.best_prey_fitness = None
        if self.best_prey_weights is not None:
            self.best_prey_fitness = float('-inf')
            
        self.best_pred_fitness = None
        if self.best_pred_weights is not None:
            self.best_pred_fitness = float('-inf')

    def spawn_food(self):
        return [random.uniform(0, WIDTH), random.uniform(0, HEIGHT)]

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Mouse hover logic for energy preview
            mx, my = pygame.mouse.get_pos()
            found = False
            for creature in self.creatures:
                if creature.alive:
                    dx = mx - int(creature.x)
                    dy = my - int(creature.y)
                    # Use size for hover radius
                    c_radius = 10 * np.sqrt(creature.size)
                    if dx*dx + dy*dy <= c_radius**2:
                        self.energy_preview_creature = creature
                        found = True
                        break
            if not found:
                self.energy_preview_creature = None

            self.season_timer += 1
            if self.season_timer > 600:
                self.is_winter = not self.is_winter
                self.season_timer = 0
                
            progress = min(1.0, self.season_timer / 120.0)  # 2 second transition
            winter_bg = (15, 25, 45)
            summer_bg = (15, 20, 15)
            
            def lerp(c1, c2, t):
                return (int(c1[0] + (c2[0] - c1[0]) * t),
                        int(c1[1] + (c2[1] - c1[1]) * t),
                        int(c1[2] + (c2[2] - c1[2]) * t))
            
            if self.is_winter:
                bg_color = lerp(summer_bg, winter_bg, progress)
            else:
                # If first generation just started, force summer immediately
                if self.generation == 1:
                    bg_color = summer_bg
                else:
                    bg_color = lerp(winter_bg, summer_bg, progress)
                
            self.screen.fill(bg_color)
            
            # Subtle grid
            for x_line in range(0, WIDTH, 50):
                pygame.draw.line(self.screen, (30, 35, 40), (x_line, 0), (x_line, HEIGHT))
            for y_line in range(0, HEIGHT, 50):
                pygame.draw.line(self.screen, (30, 35, 40), (0, y_line), (WIDTH, y_line))

            self.update()
            self.draw()

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

    def update(self):
        new_offspring = []
        for creature in self.creatures:
            if creature.alive:
                prey_l = [c for c in self.creatures if c.alive and not c.is_predator and c is not creature]
                pred_l = [c for c in self.creatures if c.alive and c.is_predator and c is not creature]
                # Calculate hearing level
                my_species = pred_l if creature.is_predator else prey_l
                hearing_level = 0.0
                for s in my_species:
                    if s.shout_intensity > 0.01:
                        dist = np.sqrt((s.x - creature.x)**2 + (s.y - creature.y)**2)
                        if dist > 0:
                            hearing_level += s.shout_intensity / max(1.0, (dist / 10.0))
                hearing_level = min(1.0, hearing_level)
                
                creature.update(self.food, prey_l, pred_l, WIDTH, HEIGHT, is_winter=self.is_winter, hearing_level=hearing_level)
                
                eaten_idx = creature.check_eat(self.food, prey_l)
                if eaten_idx is not None:
                    self.food[eaten_idx] = self.spawn_food()
                
                # Mating mechanics
                if creature.mating_cooldown == 0 and creature.energy > 80 and creature.mating_urge > 0.5:
                    my_species = pred_l if creature.is_predator else prey_l
                    c_radius = 10 * np.sqrt(creature.size)
                    for mate in my_species:
                        if mate.mating_cooldown == 0 and mate.energy > 80 and mate.mating_urge > 0.5:
                            mate_radius = 10 * np.sqrt(mate.size)
                            dist_sq = (creature.x - mate.x)**2 + (creature.y - mate.y)**2
                            if dist_sq < (c_radius + mate_radius)**2:
                                # They collided and both want to mate
                                creature.energy -= 40
                                mate.energy -= 40
                                creature.mating_cooldown = 100
                                mate.mating_cooldown = 100
                                
                                # Spawn child
                                child_brain = NeuralNetwork.crossover(creature.brain, mate.brain)
                                child_brain.mutate(self.ga.mutation_rate, self.ga.mutation_strength)
                                child_size = max(0.5, (creature.size + mate.size)/2 + np.random.uniform(-0.1, 0.1))
                                child_vision = max(50.0, (creature.vision_range + mate.vision_range)/2 + np.random.uniform(-20, 20))
                                child_fov = max(0.5, min(np.pi*2, (creature.fov + mate.fov)/2 + np.random.uniform(-0.5, 0.5)))
                                
                                child = Creature(creature.x, creature.y, energy=100, brain=child_brain, 
                                                 is_predator=creature.is_predator, size=child_size,
                                                 vision_range=child_vision, fov=child_fov)
                                child.angle = creature.angle + np.random.uniform(-0.5, 0.5)
                                
                                # 5% swap logic
                                if random.random() < 0.05:
                                    child.is_predator = not child.is_predator
                                    if child.is_predator and self.best_pred_weights is not None:
                                        child.brain.set_weights(self.best_pred_weights)
                                    elif not child.is_predator and self.best_prey_weights is not None:
                                        child.brain.set_weights(self.best_prey_weights)
                                    child.brain.mutate(self.ga.mutation_rate, self.ga.mutation_strength)
                                    
                                new_offspring.append(child)
                                break
        
        if new_offspring:
            self.creatures.extend(new_offspring)

        if all(not c.alive for c in self.creatures):
            preyl = [c for c in self.creatures if not c.is_predator]
            predl = [c for c in self.creatures if c.is_predator]
            
            if preyl:
                best_prey = max(preyl, key=lambda c: c.get_fitness())
                self.prev_champion_weights = best_prey.brain.get_weights()
                prey_fit = best_prey.get_fitness()
                if self.best_prey_fitness is None or prey_fit > self.best_prey_fitness:
                    save_brain(best_prey.brain, self.best_prey_file)
                    self.best_prey_fitness = prey_fit
                    
            if predl:
                best_pred = max(predl, key=lambda c: c.get_fitness())
                pred_fit = best_pred.get_fitness()
                if self.best_pred_fitness is None or pred_fit > self.best_pred_fitness:
                    save_brain(best_pred.brain, self.best_predator_file)
                    self.best_pred_fitness = pred_fit
                    
            self.next_generation()
            
        self.graph_timer += 1
        if self.graph_timer > 5:
            self.graph_timer = 0
            alive_prey = sum(1 for c in self.creatures if c.alive and not c.is_predator)
            alive_pred = sum(1 for c in self.creatures if c.alive and c.is_predator)
            self.graph_data_prey.append(alive_prey)
            self.graph_data_pred.append(alive_pred)
            if len(self.graph_data_prey) > 200:
                self.graph_data_prey.pop(0)
                self.graph_data_pred.pop(0)

    def next_generation(self):
        new_creatures = self.ga.next_generation(self.creatures)
        for c in new_creatures:
            c.x = random.uniform(0, WIDTH)
            c.y = random.uniform(0, HEIGHT)
        self.creatures = new_creatures
        self.generation += 1
        self.season_timer = 0
        self.is_winter = False
        self.food = [self.spawn_food() for _ in range(self.food_count)]

    def draw(self):
        # Draw glowing food
        for fx, fy in self.food:
            pygame.draw.circle(self.screen, (20, 100, 40), (int(fx), int(fy)), 8, 2)
            pygame.draw.circle(self.screen, (80, 255, 120), (int(fx), int(fy)), 4)
            
        # Draw creatures
        for creature in self.creatures:
            if creature.alive:
                color = (250, 70, 70) if creature.is_predator else (60, 160, 250)
                outline_color = (200, 40, 40) if creature.is_predator else (40, 100, 200)
            else:
                color = (70, 70, 70)
                outline_color = (50, 50, 50)
                
            x, y = int(creature.x), int(creature.y)
            radius = int(10 * np.sqrt(creature.size))
            
            # Fill
            pygame.draw.circle(self.screen, color, (x, y), max(2, radius))
            # Outline
            pygame.draw.circle(self.screen, outline_color, (x, y), max(2, radius), 2)
            
            # Visualize Shout (White ring)
            if creature.shout_intensity > 0.5:
                pygame.draw.circle(self.screen, (200, 200, 200), (x, y), int(radius) + 6, 1)
                
            # Visualize Mating Urge (Pink core or heart)
            if creature.mating_urge > 0.5 and creature.energy > 80:
                pygame.draw.circle(self.screen, (255, 105, 180), (x, y), max(2, int(radius)//2))
            
            # Draw direction nose
            if creature.alive:
                end_x = x + int(np.cos(creature.angle) * (radius + 6))
                end_y = y + int(np.sin(creature.angle) * (radius + 6))
                pygame.draw.line(self.screen, outline_color, (x, y), (end_x, end_y), 3)
                
                # Optional: subtle FOV outline for hovered creature
                if self.energy_preview_creature is creature:
                    left_angle = creature.angle - creature.fov/2
                    right_angle = creature.angle + creature.fov/2
                    vr = creature.vision_range
                    lx = x + int(np.cos(left_angle) * vr)
                    ly = y + int(np.sin(left_angle) * vr)
                    rx = x + int(np.cos(right_angle) * vr)
                    ry = y + int(np.sin(right_angle) * vr)
                    pygame.draw.line(self.screen, (100, 100, 100), (x, y), (lx, ly), 1)
                    pygame.draw.line(self.screen, (100, 100, 100), (x, y), (rx, ry), 1)
                
            # Draw energy bar above creature
            bar_width = 18
            bar_height = 3
            bar_x = x - bar_width // 2
            bar_y = y - 16
            energy_ratio = max(0, min(1, creature.energy / 100))
            fill_width = int(bar_width * energy_ratio)
            pygame.draw.rect(self.screen, (60, 60, 60),
                             (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, (0, 220, 0),
                             (bar_x, bar_y, fill_width, bar_height))
            # Draw energy value if this is the hovered creature
            if creature.alive and self.energy_preview_creature is creature:
                font = pygame.font.SysFont(None, 22)
                text_str = f"{creature.energy:.1f}"
                shadow = font.render(text_str, True, (0, 0, 0))
                self.screen.blit(shadow, (x + int(radius) + 7, y - 7))
                energy_text = font.render(text_str, True, (255, 230, 80))
                self.screen.blit(energy_text, (x + int(radius) + 6, y - 8))
        # Draw crown on previous champion if exists
        if hasattr(self, 'prev_champion_weights') and self.prev_champion_weights is not None:
            # Find the creature in the current population with the same brain weights
            def weights_equal(w1, w2):
                return all(np.allclose(a, b) for a, b in zip(w1, w2))
            champion = next((c for c in self.creatures if weights_equal(
                c.brain.get_weights(), self.prev_champion_weights)), None)
            if champion is not None:
                x, y = int(champion.x), int(champion.y)
                crown_offset = 32  # increased distance above creature center
                crown_base_y = y - crown_offset
                crown_width = 14
                crown_height = 8
                base_rect = pygame.Rect(
                    x - crown_width // 2, crown_base_y + crown_height, crown_width, 3)
                pygame.draw.rect(self.screen, (220, 200, 0), base_rect)
                points = [
                    (x - crown_width // 2, crown_base_y + crown_height),
                    (x - crown_width // 4, crown_base_y),
                    (x, crown_base_y + crown_height // 2),
                    (x + crown_width // 4, crown_base_y),
                    (x + crown_width // 2, crown_base_y + crown_height)
                ]
                pygame.draw.polygon(self.screen, (255, 215, 0), points)
        # Translucent stats panel
        panel_surf = pygame.Surface((220, 110))
        panel_surf.set_alpha(180)
        panel_surf.fill((20, 20, 20))
        self.screen.blit(panel_surf, (10, 10))
        pygame.draw.rect(self.screen, (100, 100, 100), (10, 10, 220, 110), 1)
        
        font = pygame.font.SysFont("Trebuchet MS", 24, bold=True)
        text = font.render(f"Gen {self.generation}", True, (255, 255, 255))
        self.screen.blit(text, (20, 20))
        
        season_str = "Winter" if self.is_winter else "Summer"
        season_color = (150, 200, 255) if self.is_winter else (255, 200, 100)
        s_text = pygame.font.SysFont("Trebuchet MS", 20).render(f"Season: {season_str}", True, season_color)
        self.screen.blit(s_text, (20, 50))
        
        counts_font = pygame.font.SysFont("Trebuchet MS", 18)
        prey_c = counts_font.render(f"Prey: {len([c for c in self.creatures if not c.is_predator and c.alive])}", True, (60, 160, 250))
        pred_c = counts_font.render(f"Predators: {len([c for c in self.creatures if c.is_predator and c.alive])}", True, (250, 70, 70))
        self.screen.blit(prey_c, (20, 75))
        self.screen.blit(pred_c, (120, 75))
        
        # --- Draw Graph ---
        graph_bg = pygame.Surface((200, 100))
        graph_bg.set_alpha(180)
        graph_bg.fill((20, 20, 20))
        self.screen.blit(graph_bg, (WIDTH - 220, HEIGHT - 120))
        
        graph_rect = pygame.Rect(WIDTH - 220, HEIGHT - 120, 200, 100)
        pygame.draw.rect(self.screen, (200, 200, 200), graph_rect, 1)
        
        max_val = max(10, max(self.graph_data_prey + self.graph_data_pred + [1]))
        if len(self.graph_data_prey) > 1:
            for i in range(len(self.graph_data_prey) - 1):
                x1 = WIDTH - 220 + i
                x2 = WIDTH - 220 + i + 1
                
                y1_prey = HEIGHT - 20 - int((self.graph_data_prey[i] / max_val) * 100)
                y2_prey = HEIGHT - 20 - int((self.graph_data_prey[i+1] / max_val) * 100)
                pygame.draw.line(self.screen, (0, 128, 255), (x1, y1_prey), (x2, y2_prey), 2)
                
                y1_pred = HEIGHT - 20 - int((self.graph_data_pred[i] / max_val) * 100)
                y2_pred = HEIGHT - 20 - int((self.graph_data_pred[i+1] / max_val) * 100)
                pygame.draw.line(self.screen, (255, 50, 50), (x1, y1_pred), (x2, y2_pred), 2)
        
        graph_title = pygame.font.SysFont(None, 18).render(f"Populations (Max: {max_val})", True, (200, 200, 200))
        self.screen.blit(graph_title, (WIDTH - 215, HEIGHT - 115))
