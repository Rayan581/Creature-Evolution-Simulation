from classes.brain_io import save_brain, load_brain
import pygame
from config import *

import numpy as np
import random
from classes.creature import Creature
from classes.food import FoodItem
from classes.genetic_algorithm import GeneticAlgorithm
from classes.neural_network import NeuralNetwork


class Game:
    def __init__(self):
        self.energy_preview_creature = None
        self.focused_creature = None
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.width, self.height = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.speed_multiplier = 1
        # Simulation parameters
        self.population_size = POPULATION_SIZE
        self.food_count = FOOD_COUNT
        self.best_brain_file = "best_unified_brain.pkl"
        
        if BRAIN_IO_MODE == "LOAD_AND_SAVE":
            data = load_brain(self.best_brain_file)
            if data is not None:
                self.best_brain_weights = data["weights"]
                self.best_brain_fitness = data["fitness"]
                print(f"Loaded brain from {self.best_brain_file} (Fitness: {self.best_brain_fitness:.1f})")
                if self.best_brain_weights[0].shape[0] != 26:
                    self.best_brain_weights = None
                    self.best_brain_fitness = None
            else:
                self.best_brain_weights = None
                self.best_brain_fitness = None
        else:
            self.best_brain_weights = None
            self.best_brain_fitness = None
            
        self.creatures = []
        self.population_archive = []
        spawned_elite = 0
        
        for i in range(self.population_size):
            start_omni = random.uniform(0, 1)
            c = Creature(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), omnivore=start_omni)
            
            if self.best_brain_weights is not None and spawned_elite < (self.population_size // 4):
                c.brain.set_weights(self.best_brain_weights)
                c.brain.mutate(mutation_rate=0.2, mutation_strength=0.5)
                spawned_elite += 1
                
            self.creatures.append(c)
            self.population_archive.append(c)
        self.season_timer = 0
        self.is_winter = False
        self.food = [self.spawn_food() for _ in range(self.food_count)]
        self.ga = GeneticAlgorithm(population_size=self.population_size)
        self.generation = 1
        self.graph_data_prey = []
        self.graph_data_pred = []
        self.graph_timer = 0
        self.prev_champion = None  # Track top performer from previous gen
        # Only set fallback fitness if it was NOT already loaded from file
        if not hasattr(self, 'best_brain_fitness') or self.best_brain_fitness is None:
            self.best_brain_fitness = float('-inf') if self.best_brain_weights is not None else None

        self.focus_toggle = False
        self.manual_focus = False
        self.smart_speed = False
        self.smart_speed_rect = pygame.Rect(20, 115, 180, 25)
        self.regrowth_queue = []  # list of countdown timers for grass regrowth

    def spawn_food(self):
        x = random.uniform(0, self.width)
        y = random.uniform(0, self.height)
        # In Winter, a fraction of food spawns as hardy berries
        if self.is_winter and random.random() < WINTER_BERRY_RATIO:
            return FoodItem(x, y, FoodItem.TYPE_BERRY)
        return FoodItem(x, y, FoodItem.TYPE_GRASS)

    def spawn_meat_drop(self, x, y):
        """Create a meat pile at a dead creature's position."""
        self.food.append(FoodItem(x, y, FoodItem.TYPE_MEAT))

    def save_champion(self):
        if BRAIN_IO_MODE in ["LOAD_AND_SAVE", "NEW_AND_SAVE"] and self.population_archive:
            best_c = max(self.population_archive, key=lambda c: c.get_fitness())
            self.prev_champion_weights = best_c.brain.get_weights()
            b_fit = best_c.get_fitness()
            if self.best_brain_fitness is None or b_fit > self.best_brain_fitness:
                save_brain(best_c.brain, b_fit, self.best_brain_file)
                self.best_brain_fitness = b_fit
                print(f"Gen {self.generation}: New champion saved (Fitness: {b_fit:.1f})")

    def run(self):
        while self.running:
            mouse_clicked = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_champion()
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.save_champion()
                        self.running = False
                    elif event.key == pygame.K_UP:
                        self.speed_multiplier = min(100, self.speed_multiplier + 1)
                    elif event.key == pygame.K_DOWN:
                        self.speed_multiplier = max(1, self.speed_multiplier - 1)
                    elif event.key == pygame.K_r:
                        # R only works if we aren't manually focused on something
                        if not self.manual_focus:
                            self.focus_toggle = not self.focus_toggle
                            if not self.focus_toggle:
                                self.focused_creature = None
                    elif event.key == pygame.K_s:
                        self.smart_speed = not self.smart_speed
                elif event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.w, event.h
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_clicked = True
                    if self.smart_speed_rect.collidepoint(event.pos):
                        self.smart_speed = not self.smart_speed
                        mouse_clicked = False  # treat this as purely a UI click
            
            # Mouse hover logic for energy preview mapped to camera
            mx, my = pygame.mouse.get_pos()
            cam_offset_x = 0
            cam_offset_y = 0
            if getattr(self, 'focused_creature', None) and self.focused_creature.alive:
                cam_offset_x = self.width/2 - self.focused_creature.x
                cam_offset_y = self.height/2 - self.focused_creature.y

            found = False
            for creature in self.creatures:
                if creature.alive:
                    sx = creature.x + cam_offset_x
                    sy = creature.y + cam_offset_y
                    dx = mx - sx
                    dy = my - sy
                    c_radius = 10 * np.sqrt(creature.size)
                    
                    if dx*dx + dy*dy <= c_radius**2:
                        self.energy_preview_creature = creature
                        if mouse_clicked:
                            self.focused_creature = creature
                        found = True
                        break
            if not found:
                self.energy_preview_creature = None
                if mouse_clicked:
                    self.focused_creature = None
                    self.manual_focus = False
                    self.focus_toggle = False
            else:
                # We found a creature via click or hover
                if mouse_clicked:
                    self.manual_focus = True
                    self.focus_toggle = False

            # Smart Speed calculation
            if self.smart_speed:
                pop = len(self.creatures)
                # 5x speed at 5 creatures, 1x speed at FULL POPULATION
                # Linear transition
                if pop <= 5:
                    self.speed_multiplier = 5
                elif pop >= self.population_size:
                    self.speed_multiplier = 1
                else:
                    ratio = (pop - 5) / (self.population_size - 5)
                    self.speed_multiplier = int(max(1, min(5, 5 - ratio * 4)))

            self.season_timer += 1
            if self.season_timer > SEASON_LENGTH:
                self.is_winter = not self.is_winter
                self.season_timer = 0
                
            progress = min(1.0, self.season_timer / 120.0)  # 2 second transition
            winter_bg = Colors.WINTER_BG
            summer_bg = Colors.SUMMER_BG
            
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
            
            # Subtle moving grid
            cx, cy = 0, 0
            if self.focused_creature and self.focused_creature.alive:
                cx = self.width/2 - self.focused_creature.x
                cy = self.height/2 - self.focused_creature.y
                
            grid_offset_x = int(cx) % 50
            grid_offset_y = int(cy) % 50
            
            for x_line in range(grid_offset_x, self.width, 50):
                pygame.draw.line(self.screen, Colors.GRID_LINE, (x_line, 0), (x_line, self.height))
            for y_line in range(grid_offset_y, self.height, 50):
                pygame.draw.line(self.screen, Colors.GRID_LINE, (0, y_line), (self.width, y_line))

            for _ in range(self.speed_multiplier):
                self.update()

            if self.focus_toggle:
                alive_creatures = [c for c in self.creatures if c.alive]
                if alive_creatures:
                    self.focused_creature = max(alive_creatures, key=lambda c: c.get_fitness())
                
            self.draw()

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

    def update(self):
        new_offspring = []
        
        # Prune dead creatures from the active list; spawn meat drops
        alive_now = []
        for c in self.creatures:
            if c.alive:
                alive_now.append(c)
            else:
                # Leave a meat drop at death location
                self.spawn_meat_drop(c.x, c.y)
        self.creatures = alive_now
        
        for creature in self.creatures:
            if creature.alive:
                other_creatures = [c for c in self.creatures if c is not creature]
                
                # Calculate hearing level
                hearing_level = 0.0
                for s in other_creatures:
                    if s.shout_intensity > 0.01:
                        dist = np.sqrt((s.x - creature.x)**2 + (s.y - creature.y)**2)
                        if dist > 0:
                            hearing_level += s.shout_intensity / max(1.0, (dist / 10.0))
                hearing_level = min(1.0, hearing_level)
                
                creature.update(self.food, other_creatures, self.width, self.height, is_winter=self.is_winter, hearing_level=hearing_level)
                
                eaten_idx = creature.check_eat(self.food, other_creatures)
                if eaten_idx is not None:
                    eaten = self.food.pop(eaten_idx)
                    # Only grass triggers a regrowth timer; berries/meat don't respawn
                    if eaten.type == FoodItem.TYPE_GRASS:
                        self.regrowth_queue.append(FOOD_REGROWTH_DELAY)
                
                # Mating mechanics
                if creature.mating_cooldown == 0 and creature.energy > MATING_ENERGY_THRESHOLD and creature.mating_urge > 0.5:
                    c_radius = 10 * np.sqrt(creature.size)
                    for mate in other_creatures:
                        if mate.mating_cooldown == 0 and mate.energy > MATING_ENERGY_THRESHOLD and mate.mating_urge > 0.5:
                            mate_radius = 10 * np.sqrt(mate.size)
                            dist_sq = (creature.x - mate.x)**2 + (creature.y - mate.y)**2
                            if dist_sq < (c_radius + mate_radius)**2:
                                # They collided and both want to mate
                                creature.energy -= MATING_ENERGY_COST
                                mate.energy -= MATING_ENERGY_COST
                                creature.mating_cooldown = MATING_COOLDOWN_FRAMES
                                mate.mating_cooldown = MATING_COOLDOWN_FRAMES
                                
                                # Add fitness bonus for successful mating
                                creature.bonus_fitness += MATING_FITNESS_BONUS
                                mate.bonus_fitness += MATING_FITNESS_BONUS
                                
                                # Spawn child
                                child_brain = NeuralNetwork.crossover(creature.brain, mate.brain)
                                child_brain.mutate(self.ga.mutation_rate, self.ga.mutation_strength)
                                child_size = max(0.5, (creature.size + mate.size)/2 + np.random.uniform(-0.1, 0.1))
                                child_vision = max(50.0, (creature.vision_range + mate.vision_range)/2 + np.random.uniform(-20, 20))
                                child_fov = max(0.5, min(np.pi, (creature.fov + mate.fov)/2 + np.random.uniform(-0.5, 0.5)))
                                child_omni = max(0.0, min(1.0, (creature.omnivore + mate.omnivore)/2 + np.random.uniform(-0.1, 0.1)))
                                
                                child = Creature(creature.x, creature.y, energy=STARTING_ENERGY, brain=child_brain, 
                                                 size=child_size, vision_range=child_vision, fov=child_fov, omnivore=child_omni)
                                child.angle = creature.angle + np.random.uniform(-0.5, 0.5)
                                
                                new_offspring.append(child)
                                break
        
        if new_offspring:
            self.creatures.extend(new_offspring)
            self.population_archive.extend(new_offspring)

        # Tick food decay and remove dead items; count how many to re-seed
        prev_grass = sum(1 for f in self.food if f.type != FoodItem.TYPE_MEAT)
        self.food = [f for f in self.food if not f.is_dead]
        for f in self.food:
            f.tick()

        # Regrowth queue: tick down timers, spawn new grass when ready
        self.regrowth_queue = [t - 1 for t in self.regrowth_queue]
        ready = [t for t in self.regrowth_queue if t <= 0]
        self.regrowth_queue = [t for t in self.regrowth_queue if t > 0]
        for _ in ready:
            self.food.append(self.spawn_food())

        if not self.creatures:
            if self.population_archive:
                self.save_champion()
                    
            self.next_generation()
            
        self.graph_timer += 1
        if self.graph_timer > 5:
            self.graph_timer = 0
            alive_c = [c.omnivore for c in self.creatures if c.alive]
            avg_omni = sum(alive_c) / len(alive_c) if alive_c else 0
            self.graph_data_prey.append(avg_omni * 10)
            self.graph_data_pred.append(0)
            if len(self.graph_data_prey) > 200:
                self.graph_data_prey.pop(0)
                self.graph_data_pred.pop(0)

    def next_generation(self):
        new_creatures = self.ga.next_generation(self.population_archive)
        for c in new_creatures:
            c.x = random.uniform(0, self.width)
            c.y = random.uniform(0, self.height)
        self.creatures = new_creatures
        self.population_archive = list(new_creatures)
        self.generation += 1
        self.season_timer = 0
        self.is_winter = False
        self.food = [self.spawn_food() for _ in range(self.food_count)]

    def draw(self):
        def to_screen(px, py):
            if self.focused_creature and self.focused_creature.alive:
                # Add camera offset
                cx = self.width/2 - self.focused_creature.x
                cy = self.height/2 - self.focused_creature.y
                return int(px + cx), int(py + cy)
            return int(px), int(py)
            
        # Draw food items with decay gradient
        for food in self.food:
            sx, sy = to_screen(food.x, food.y)
            r = food.radius()
            inner_color = food.color
            if food.type == FoodItem.TYPE_MEAT:
                # Meat: draw a solid filled circle, slightly larger
                pygame.draw.circle(self.screen, inner_color, (sx, sy), r + 2)
            else:
                # Grass / Berry: outer ring + inner dot
                outer_color = tuple(max(0, c - 60) for c in inner_color)
                pygame.draw.circle(self.screen, outer_color, (sx, sy), r + 3, 2)
                pygame.draw.circle(self.screen, inner_color, (sx, sy), r)
            
        # Draw active creatures
        for creature in self.creatures:
            # Lerp from PREY color to PREDATOR color based on omnivore val
            r1, g1, b1 = Colors.PREY
            r2, g2, b2 = Colors.PREDATOR
            omni = creature.omnivore
            color = (int(r1 + (r2-r1)*omni), int(g1 + (g2-g1)*omni), int(b1 + (b2-b1)*omni))
            
            ro1, go1, bo1 = Colors.PREY_OUTLINE
            ro2, go2, bo2 = Colors.PREDATOR_OUTLINE
            outline_color = (int(ro1 + (ro2-ro1)*omni), int(go1 + (go2-go1)*omni), int(bo1 + (bo2-bo1)*omni))
                
            x, y = to_screen(creature.x, creature.y)
            radius = int(10 * np.sqrt(creature.size))
            
            # Fill
            pygame.draw.circle(self.screen, color, (x, y), max(2, radius))
            # Outline
            pygame.draw.circle(self.screen, outline_color, (x, y), max(2, radius), 2)
            
            # Visualize Shout (White ring)
            if creature.shout_intensity > 0.5:
                pygame.draw.circle(self.screen, Colors.SHOUT_RING, (x, y), int(radius) + 6, 1)
                
            # Visualize Mating Urge (Pink core or heart)
            if creature.mating_urge > 0.5 and creature.energy > MATING_ENERGY_THRESHOLD:
                pygame.draw.circle(self.screen, Colors.MATING_CORE, (x, y), max(2, int(radius)//2))
            
            # Draw direction nose
            end_x, end_y = to_screen(creature.x + np.cos(creature.angle) * (radius + 6), creature.y + np.sin(creature.angle) * (radius + 6))
            pygame.draw.line(self.screen, outline_color, (x, y), (end_x, end_y), 3)
                
            # Draw FOV cone arc for hovered creature
            if self.energy_preview_creature is creature or self.focused_creature is creature:
                vr = creature.vision_range
                points = [(x, y)]
                # Create a smooth arc of points along the fov
                arc_angles = np.linspace(creature.angle - creature.fov/2, creature.angle + creature.fov/2, 10)
                for a in arc_angles:
                    px, py = to_screen(creature.x + np.cos(a) * vr, creature.y + np.sin(a) * vr)
                    points.append((px, py))
                    
                # Create a transparent surface to draw the cone locally
                cone_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(cone_surf, Colors.FOV_CONE, points)
                self.screen.blit(cone_surf, (0, 0))
                
            # Draw energy bar above creature
            bar_width = 18
            bar_height = 3
            bar_x = x - bar_width // 2
            bar_y = y - 16
            energy_ratio = max(0, min(1, creature.energy / STARTING_ENERGY))
            fill_width = int(bar_width * energy_ratio)
            pygame.draw.rect(self.screen, Colors.ENERGY_BAR_BG,
                             (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, Colors.ENERGY_BAR_FILL,
                             (bar_x, bar_y, fill_width, bar_height))
            # Draw energy value if this is the hovered creature
            if self.energy_preview_creature is creature or self.focused_creature is creature:
                font = pygame.font.SysFont(None, 22)
                text_str = f"{creature.energy:.1f}"
                shadow = font.render(text_str, True, Colors.ENERGY_LABEL_SHADOW)
                self.screen.blit(shadow, (x + int(radius) + 7, y - 7))
                energy_text = font.render(text_str, True, Colors.ENERGY_LABEL)
                self.screen.blit(energy_text, (x + int(radius) + 6, y - 8))

                # Draw fitness score under the focused creature
                font = pygame.font.SysFont(None, 16)
                fitness_str = f"{creature.get_fitness():.1f}"
                shadow = font.render(fitness_str, True, Colors.ENERGY_LABEL_SHADOW)
                self.screen.blit(shadow, (x - 10, y + int(radius) + 6))
                fitness_text = font.render(fitness_str, True, Colors.ENERGY_LABEL)
                self.screen.blit(fitness_text, (x - 10, y + int(radius) + 7))

        # Translucent stats panel
        panel_surf = pygame.Surface((220, 150))
        panel_surf.set_alpha(180)
        panel_surf.fill(Colors.PANEL_BG)
        self.screen.blit(panel_surf, (10, 10))
        pygame.draw.rect(self.screen, Colors.PANEL_BORDER, (10, 10, 220, 150), 1)
        
        font = pygame.font.SysFont("Trebuchet MS", 24, bold=True)
        text = font.render(f"Gen {self.generation}", True, Colors.UI_GEN_LABEL)
        self.screen.blit(text, (20, 20))
        
        season_str = "Winter" if self.is_winter else "Summer"
        season_color = Colors.UI_SEASON_WINTER if self.is_winter else Colors.UI_SEASON_SUMMER
        s_text = pygame.font.SysFont("Trebuchet MS", 20).render(f"Season: {season_str}", True, season_color)
        self.screen.blit(s_text, (20, 50))
        
        counts_font = pygame.font.SysFont("Trebuchet MS", 18)
        speed_text = counts_font.render(f"Speed: {self.speed_multiplier}x", True, Colors.UI_TEXT)
        self.screen.blit(speed_text, (20, 90))
        
        # Smart Speed Button
        btn_color = (100, 255, 100) if self.smart_speed else (150, 150, 150)
        pygame.draw.rect(self.screen, (40, 40, 40), self.smart_speed_rect)
        pygame.draw.rect(self.screen, btn_color, self.smart_speed_rect, 1)
        
        btn_text = "Smart Speed: ON" if self.smart_speed else "Smart Speed: OFF"
        s_btn_font = pygame.font.SysFont("Trebuchet MS", 16, bold=self.smart_speed)
        s_btn_surf = s_btn_font.render(btn_text, True, btn_color)
        self.screen.blit(s_btn_surf, (self.smart_speed_rect.centerx - s_btn_surf.get_width()//2, 
                                     self.smart_speed_rect.centery - s_btn_surf.get_height()//2))
        
        total_alive = sum(1 for c in self.creatures if c.alive)
        pop_c = counts_font.render(f"Alive: {total_alive}", True, Colors.UI_TEXT)
        self.screen.blit(pop_c, (20, 75))
        
        # --- Draw Graph ---
        graph_bg = pygame.Surface((200, 100))
        graph_bg.set_alpha(180)
        graph_bg.fill(Colors.PANEL_BG)
        self.screen.blit(graph_bg, (WIDTH - 220, HEIGHT - 120))
        
        graph_rect = pygame.Rect(WIDTH - 220, HEIGHT - 120, 200, 100)
        pygame.draw.rect(self.screen, Colors.PANEL_BORDER, graph_rect, 1)
        
        max_val = max(10, max(self.graph_data_prey + self.graph_data_pred + [1]))
        if len(self.graph_data_prey) > 1:
            for i in range(len(self.graph_data_prey) - 1):
                x1 = WIDTH - 220 + i
                x2 = WIDTH - 220 + i + 1
                
                y1_prey = HEIGHT - 20 - int((self.graph_data_prey[i] / max_val) * 100)
                y2_prey = HEIGHT - 20 - int((self.graph_data_prey[i+1] / max_val) * 100)
                pygame.draw.line(self.screen, Colors.GRAPH_LINE, (x1, y1_prey), (x2, y2_prey), 2)
        
        graph_title = pygame.font.SysFont(None, 18).render(f"Omnivore Spectrum x10", True, Colors.UI_TEXT)
        self.screen.blit(graph_title, (WIDTH - 215, HEIGHT - 115))
        
        # --- Draw Neural Network Sidebar if focused ---
        if self.focused_creature and self.focused_creature.alive:
            sidebar = pygame.Surface((300, HEIGHT))
            sidebar.set_alpha(240)
            sidebar.fill(Colors.NN_BG)
            self.screen.blit(sidebar, (WIDTH - 300, 0))
            pygame.draw.line(self.screen, Colors.NN_BORDER, (WIDTH - 300, 0), (WIDTH - 300, HEIGHT), 2)
            
            title = font.render(f"Brain Scan", True, Colors.NN_TITLE)
            self.screen.blit(title, (WIDTH - 280, 20))
            
            weights = self.focused_creature.brain.get_weights()
            if weights and len(weights) >= 4:
                w1, b1, w2, b2 = weights
                
                in_nodes = self.focused_creature.brain.input_size
                hid_nodes = self.focused_creature.brain.hidden_size
                out_nodes = self.focused_creature.brain.output_size
                
                def draw_layer_nodes(x_pos, node_count, color=(100, 100, 100)):
                    spacing = min(15, (HEIGHT - 100) / max(1, node_count))
                    start_y = HEIGHT/2 - (spacing * node_count)/2
                    nodes_pos = []
                    for i in range(node_count):
                        py = start_y + i * spacing
                        pygame.draw.circle(self.screen, color, (x_pos, int(py)), 3)
                        nodes_pos.append((x_pos, int(py)))
                    return nodes_pos
                    
                in_points = draw_layer_nodes(WIDTH - 260, in_nodes, Colors.NN_NODES_IN)
                hid_points = draw_layer_nodes(WIDTH - 150, hid_nodes, Colors.NN_NODES_HIDDEN)
                out_points = draw_layer_nodes(WIDTH - 40, out_nodes, Colors.NN_NODES_OUT)
                
                # Output labels
                labels = ["Rot", "Spd", "Sht", "Mat"]
                lbl_font = pygame.font.SysFont(None, 16)
                for i, (px, py) in enumerate(out_points):
                    if i < len(labels):
                        lbl = lbl_font.render(labels[i], True, Colors.NN_LABEL)
                        self.screen.blit(lbl, (px - 25, py - 18))
                        
                # Draw dominant connections (w2) to prevent lag
                for h in range(hid_nodes):
                    for o in range(out_nodes):
                        weight = w2[h, o]
                        if abs(weight) > 1.0:
                            c = Colors.NN_WEIGHT_POS if weight > 0 else Colors.NN_WEIGHT_NEG
                            pygame.draw.line(self.screen, c, hid_points[h], out_points[o], 1)
