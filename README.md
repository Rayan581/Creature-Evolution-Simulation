# Creature Evolution Simulation 2.0

A sophisticated artificial life ecosystem where Neural-Network-driven creatures evolve fluid survival strategies on a continuous omnivore spectrum.

![Status](https://img.shields.io/badge/Status-Fully%20Functional-brightgreen)
![Engine](https://img.shields.io/badge/Engine-Python%20%2F%20Pygame-blue)

## 🧬 Evolutionary Features

### Unified Omnivore Spectrum
The rigid "Predator vs Prey" labels have been replaced by a continuous **Omnivore Trait** (0.0 to 1.0). 
- **Blue (0.0):** Pure Herbivores. Gain maximum energy from grass but cannot digest meat.
- **Red (1.0):** Pure Carnivores. Gain maximum energy from meat but cannot eat grass.
- **Purple (0.5):** Omnivores. Can eat both but with reduced efficiency.
- **Dynamic Hunting:** A creature can hunt and eat any other creature as long as its omnivore score is at least **0.2 higher** than its target's. This allows complex multi-tiered food chains to emerge naturally.

### Neural Network Genetics
Each creature's brain is a Neural Network (26 inputs, 16 hidden, 4 outputs):
- **Sensory Inputs:** 24-ray vision (detecting food proximity, creature proximity, and target omnivore scores), energy reserves, and hearing.
- **Action Outputs:** Rotation (turning), Speed (movement), Shout Intensity (audio signal), and Mating Urge.
- **Heredity:** Successful survivors pass their traits (size, FOV, vision range, and omnivore score) and neural weights to the next generation via genetic crossover and mutation.

### Social Audio & Physical Mating
- **Communication:** Creatures can "Shout" (white pulsating rings) which others of the same lineage can "Hear," enabling potential herd or pack behaviors.
- **Reproduction:** Creatures do not clone. They must maintain high energy, broadcast a "Mating Urge" (pink core), and physically collide with a partner to spawn a mutated child.

### Adaptive Seasons
The simulation cycles between **Summer** and **Winter**. Environment colors and energy drains shift, forcing the population to adapt to seasonal scarcity or perish.

---

## 🖥️ Interactive UI & Controls

### Focus Camera & Brain Scan
- **Click a Creature:** Instantly lock the camera to that creature. A dark sidebar will slide in showing a live **Brain Scan**—a real-time visualization of their neural network's architecture and firing synapses.
- **Click Background:** Unlock the camera to return to a global view.

### Advanced Time Controls
Fast-forward through millions of years of evolution using the keyboard:
- **[UP ARROW]:** Increase simulation speed (up to 100x multiplier).
- **[DOWN ARROW]:** Decrease simulation speed (minimum 1x).
- **[R]:** Focus camera on a random living creature.
- **[ESC]:** Exit simulation.

### Centralized Configuration
Tweak every aspect of the simulation in `config.py`:
- **Populations:** Adjust `POPULATION_SIZE` and `FOOD_COUNT`.
- **Bio-Mechanics:** Dial in `ENERGY_YIELD`, `MUTATION_RATE`, and `ELITISM_COUNT`.
- **Visuals:** Edit the `Colors` class to change the entire UI palette in one place.
- **Brain I/O:** Set `BRAIN_IO_MODE` to `LOAD_AND_SAVE`, `NEW_AND_SAVE`, or `NEW_NO_SAVE`.

---

## 🚀 How to Run

1. **Install Dependencies:**
   ```bash
   pip install pygame numpy
   ```

2. **Launch Simulation:**
   ```bash
   python main.py
   ```
