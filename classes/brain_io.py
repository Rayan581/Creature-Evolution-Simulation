import pickle


def save_brain(brain, filename):
    with open(filename, 'wb') as f:
        pickle.dump(brain.get_weights(), f)


def load_brain(filename):
    import os
    if not os.path.exists(filename):
        return None
    with open(filename, 'rb') as f:
        return pickle.load(f)
