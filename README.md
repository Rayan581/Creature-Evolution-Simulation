# Creature Evolution Simulation 2.0

A sophisticated artificial life ecosystem where Neural-Network-driven creatures evolve fluid survival strategies on a continuous omnivore spectrum.

![Status](https://img.shields.io/badge/Status-Fully%20Functional-brightgreen)
![Engine](https://img.shields.io/badge/Engine-Python%20%2F%20Pygame-blue)

## 🧬 Evolutionary Features

### Unified Omnivore Spectrum
The rigid "Predator vs Prey" labels have been replaced by a continuous **Omnivore Trait** (0.0 to 1.0). 
- **Blue (0.0):** Pure Herbivores. Gain maximum energy from grass and berries.
- **Red (1.0):** Pure Carnivores. Gain maximum energy from meat and successful hunts.
- **Purple (0.5):** Omnivores. Can eat everything with varying efficiency.
- **Balanced Ecosystem:** Herbivores have metabolic advantages (lower energy drain and speed boosts), while carnivores must hunt actively for high-energy meat.

### Dynamic Food System
Food is no longer just static points. It is a living part of the ecosystem:
- **Food Types:**
    - **Grass (Green):** Higher energy (40), but only grows in Summer and decays steadily.
    - **Berries (Purple):** Medium energy (30), hardy enough to grow in Winter.
    - **Meat (Red):** High energy (75), dropped when creatures die. Only carnivores can digest this.
- **Energy Decay:** All food items lose energy over time. Their color fades from vibrant to grey as they rot, finally disappearing.
- **Regrowth Timers:** Eaten grass takes ~3 seconds to regrow, forcing creatures to move and explore.

### Neural Network Genetics & Persistence
Each creature's brain is a Neural Network (26 inputs, 16 hidden, 4 outputs):
- **Sensory Inputs:** 24-ray vision (detecting food proximity, creature proximity, and target omnivore scores), energy reserves, and hearing.
- **Action Outputs:** Rotation (turning), Speed (movement), Shout Intensity (audio signal), and Mating Urge.
- **Persistent Evolution:** The simulation tracks the **Global Elite** across generations. Only the most successful survivors' neural weights are preserved.
- **Energy-Based Fitness:** Success is measured by total energy successfully digested and survival time, rather than just raw item counts.

### Social Audio & Physical Mating
- **Communication:** Creatures can "Shout" (white pulsating rings) which others of the same lineage can "Hear," enabling herd or pack behaviors.
- **Reproduction:** Creatures must maintain high energy, broadcast a "Mating Urge" (pink core), and physically collide with a partner to spawn a mutated child.

### Adaptive Seasons & Performance
- **Seasonal Cycles:** The simulation cycles between **Summer** (lush grass) and **Winter** (scarce berries). Energy drain is higher in winter, though herbivores have better cold-resistance.
- **Engine Optimization:** Background processes automatically prune dead creature data and handle dynamic window resizing.

---

## 🖥️ Interactive UI & Controls

### Smart Focus Camera & Brain Scan
- **Click a Creature:** Instantly lock the camera to that creature. A dark sidebar will slide in showing a live **Brain Scan**—a real-time visualization of their neural network's architecture.
- **Auto-Tracking:** The camera system intelligently manages focus. If a tracked creature dies, it automatically transitions to a new high-fitness individual.
- **Click Background:** Unlock the camera to return to a global view.

### Advanced Time & Session Controls
- **[UP / DOWN ARROW]:** Adjust simulation speed (1x to 100x).
- **[S]:** Toggle **Smart Speed**. Automatically accelerates the simulation (up to 5x) when population is low and returns to 1x during population booms.
- **[R]:** Toggle **Auto-Focus** on the highest-fitness creature.
- **[ESC]:** Save progress and exit. Window is **fully resizable**—the world expands dynamically!

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
