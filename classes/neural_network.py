import numpy as np


class NeuralNetwork:
    # Inputs: 24 (rays) + 1 (energy) + 1 (hearing) = 26
    # Outputs: rot, speed, shout, mate = 4
    def __init__(self, input_size=26, hidden_size=16, output_size=4):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        # Xavier initialization
        self.w1 = np.random.randn(
            self.input_size, self.hidden_size) / np.sqrt(self.input_size)
        self.b1 = np.zeros(self.hidden_size)
        self.w2 = np.random.randn(
            self.hidden_size, self.output_size) / np.sqrt(self.hidden_size)
        self.b2 = np.zeros(self.output_size)

    def forward(self, x):
        h = np.tanh(np.dot(x, self.w1) + self.b1)
        out = np.tanh(np.dot(h, self.w2) + self.b2)
        return out

    def get_weights(self):
        return [self.w1.copy(), self.b1.copy(), self.w2.copy(), self.b2.copy()]

    def set_weights(self, weights):
        self.w1, self.b1, self.w2, self.b2 = [w.copy() for w in weights]

    def mutate(self, mutation_rate=0.05, mutation_strength=0.2):
        for param in [self.w1, self.b1, self.w2, self.b2]:
            mask = np.random.rand(*param.shape) < mutation_rate
            param += mask * np.random.randn(*param.shape) * mutation_strength

    @staticmethod
    def crossover(parent1, parent2):
        child = NeuralNetwork(parent1.input_size,
                              parent1.hidden_size, parent1.output_size)
        for i, (p1, p2) in enumerate(zip(parent1.get_weights(), parent2.get_weights())):
            mask = np.random.rand(*p1.shape) < 0.5
            child_param = np.where(mask, p1, p2)
            [child.w1, child.b1, child.w2, child.b2][i][:] = child_param
        return child
