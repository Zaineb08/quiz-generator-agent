import json
import os

class LearnerModel:
    FILE = "learner_profile.json"

    def __init__(self):
        self.profile = self.load()

    def load(self):
        if os.path.exists(self.FILE):
            with open(self.FILE, "r") as f:
                return json.load(f)
        return {"scores": {}}

    def save(self):
        with open(self.FILE, "w") as f:
            json.dump(self.profile, f, indent=2)

    def update(self, topic, correct):
        if topic not in self.profile["scores"]:
            self.profile["scores"][topic] = {"correct": 0, "total": 0}
        self.profile["scores"][topic]["total"] += 1
        if correct:
            self.profile["scores"][topic]["correct"] += 1
        self.save()

    def mastery(self, topic):
        d = self.profile["scores"].get(topic, {"correct": 0, "total": 0})
        if d["total"] == 0:
            return 0
        return (d["correct"] / d["total"]) * 100

    def level(self, topic):
        score = self.mastery(topic)
        if score >= 80:
            return "Advanced"
        elif score >= 70:
            return "Intermediate"
        return "Beginner"

    def analysis(self):
        return {
            topic: self.mastery(topic)
            for topic in self.profile["scores"]
        }
