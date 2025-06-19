class UserMemory:
    def __init__(self):
        self.memory = {"liked": [], "disliked": []}

    def like(self, title):
        if title not in self.memory["liked"]:
            self.memory["liked"].append(title)

    def dislike(self, title):
        if title not in self.memory["disliked"]:
            self.memory["disliked"].append(title)

    def get_likes(self):
        return self.memory["liked"]

    def get_dislikes(self):
        return self.memory["disliked"]

    def reset(self):
        self.memory = {"liked": [], "disliked": []}
