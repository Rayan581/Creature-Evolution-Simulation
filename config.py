WIDTH = 1200
ASPECT_RATIO = 16 / 9
HEIGHT = int(WIDTH / ASPECT_RATIO)

FPS = 60
TITLE = "Creature Evolution Simulator"

# Populations
POPULATION_SIZE = 48
FOOD_COUNT = 24

# Energy & Mechanics
STARTING_ENERGY = 100.0
FOOD_ENERGY_YIELD = 40.0
PREY_ENERGY_YIELD = 75.0

MATING_ENERGY_THRESHOLD = 80.0
MATING_ENERGY_COST = 40.0
MATING_COOLDOWN_FRAMES = 100

# Brain I/O Configuration
# "LOAD_AND_SAVE": Loads existing brains from file, saves new champions.
# "NEW_AND_SAVE": Ignores existing files (fresh start), saves new champions.
# "NEW_NO_SAVE": Ignores existing files, does NOT save to files.
BRAIN_IO_MODE = "LOAD_AND_SAVE"

# Genetics
DEFAULT_VISION_RANGE = 150.0
BASE_SPEED_MULTIPLIER = 3.5
MUTATION_RATE = 0.05
MUTATION_STRENGTH = 0.2
ELITISM_COUNT = 4

# Seasons
SEASON_LENGTH = 600

class Colors:
    # Backgrounds
    WINTER_BG = (15, 25, 45)
    SUMMER_BG = (15, 20, 15)

    # Creatures — lerped between PREY and PREDATOR based on omnivore score
    PREY = (60, 160, 250)
    PREY_OUTLINE = (40, 100, 200)
    PREDATOR = (250, 70, 70)
    PREDATOR_OUTLINE = (200, 40, 40)
    DEAD = (70, 70, 70)
    DEAD_OUTLINE = (50, 50, 50)

    # Food
    FOOD_INNER = (80, 255, 120)
    FOOD_OUTER = (20, 100, 40)

    # UI
    GRID_LINE = (30, 35, 40)
    PANEL_BG = (20, 20, 20)
    PANEL_BORDER = (100, 100, 100)
    UI_TEXT = (200, 200, 200)
    UI_GEN_LABEL = (255, 255, 255)
    UI_SEASON_WINTER = (150, 200, 255)
    UI_SEASON_SUMMER = (255, 200, 100)
    GRAPH_LINE = (200, 50, 255)

    # Creature overlays
    SHOUT_RING = (200, 200, 200)
    MATING_CORE = (255, 105, 180)
    FOV_CONE = (255, 255, 255, 30)       # RGBA — used on SRCALPHA surface
    ENERGY_BAR_BG = (60, 60, 60)
    ENERGY_BAR_FILL = (0, 220, 0)
    ENERGY_LABEL_SHADOW = (0, 0, 0)
    ENERGY_LABEL = (255, 230, 80)

    # Neural network sidebar
    NN_BG = (15, 15, 20)
    NN_BORDER = (100, 100, 100)
    NN_TITLE = (200, 255, 200)
    NN_NODES_IN = (150, 150, 250)
    NN_NODES_HIDDEN = (150, 250, 150)
    NN_NODES_OUT = (250, 150, 150)
    NN_WEIGHT_POS = (0, 255, 0)
    NN_WEIGHT_NEG = (255, 0, 0)
    NN_LABEL = (200, 200, 200)