from config import GRASS_ENERGY, BERRY_ENERGY, MEAT_ENERGY, GRASS_MAX_AGE, BERRY_MAX_AGE, MEAT_MAX_AGE, Colors


class FoodItem:
    """Represents a single food item in the simulation with decay and type support."""

    TYPE_GRASS = "grass"
    TYPE_BERRY = "berry"
    TYPE_MEAT  = "meat"

    def __init__(self, x, y, food_type=TYPE_GRASS):
        self.x = x
        self.y = y
        self.type = food_type
        self.age = 0

        if food_type == self.TYPE_GRASS:
            self.max_energy = GRASS_ENERGY
            self.max_age    = GRASS_MAX_AGE
            self._full_color = Colors.FOOD_GRASS_FULL
        elif food_type == self.TYPE_BERRY:
            self.max_energy = BERRY_ENERGY
            self.max_age    = BERRY_MAX_AGE
            self._full_color = Colors.FOOD_BERRY_FULL
        else:  # meat
            self.max_energy = MEAT_ENERGY
            self.max_age    = MEAT_MAX_AGE
            self._full_color = Colors.FOOD_MEAT_FULL

    @property
    def energy_fraction(self):
        """0.0 (dead/empty) → 1.0 (full / just spawned)."""
        return max(0.0, 1.0 - self.age / self.max_age)

    @property
    def current_energy(self):
        return self.max_energy * self.energy_fraction

    @property
    def is_dead(self):
        return self.age >= self.max_age

    @property
    def color(self):
        """Lerp from type color → dark grey as the item decays."""
        t = self.energy_fraction
        r = int(self._full_color[0] * t + Colors.FOOD_DEAD[0] * (1 - t))
        g = int(self._full_color[1] * t + Colors.FOOD_DEAD[1] * (1 - t))
        b = int(self._full_color[2] * t + Colors.FOOD_DEAD[2] * (1 - t))
        return (r, g, b)

    def tick(self, dt=1.0):
        """Advance age by delta-time."""
        self.age += dt

    def radius(self):
        """Visual radius shrinks slightly as food decays."""
        base = 4 if self.type == self.TYPE_MEAT else 4
        return max(2, int(base * (0.5 + 0.5 * self.energy_fraction)))
