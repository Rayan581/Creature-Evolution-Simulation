import pickle


def save_brain(brain, fitness, filename):
    data = {
        "weights": brain.get_weights(),
        "fitness": fitness
    }
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def load_brain(filename):
    import os
    if not os.path.exists(filename):
        return None
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        # Backward compatibility: if data is just weights (list), return as {"weights": data, "fitness": -inf}
        if isinstance(data, list):
            return {"weights": data, "fitness": float('-inf')}
        return data
