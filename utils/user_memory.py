import pickle
import os

MEMORY_PATH = "data/user_memory.pkl"

class UserMemory:
    def __init__(self):
        if os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "rb") as f:
                self.memory = pickle.load(f)
        else:
            self.memory = {"liked": [], "disliked": []}

    def save(self):
        with open(MEMORY_PATH, "wb") as f:
            pickle.dump(self.memory, f)

    def like(self, title):
        if title not in self.memory["liked"]:
            self.memory["liked"].append(title)
        self.save()

    def dislike(self, title):
        if title not in self.memory["disliked"]:
            self.memory["disliked"].append(title)
        self.save()

    def get_likes(self):
        return self.memory["liked"]

    def get_dislikes(self):
        return self.memory["disliked"]

    def reset(self):
        self.memory = {"liked": [], "disliked": []}
        self.save()


# memory = UserMemory()
