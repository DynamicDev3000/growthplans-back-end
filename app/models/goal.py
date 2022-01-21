from flask import current_app, jsonify
from app import db

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    due_date = db.Column(db.DateTime)
    why = db.Column(db.String)
##big why reflection? #foreen obstacles, tools to overcome them
    difficulty = db.Column(db.Integer)
    tasks = db.relationship("Task", backref="goal", lazy=True)
    goal_completed_at = db.Column(db.DateTime)

    COLUMNS = ["title", "due_date", "why", "difficulty"]
    
    def to_dict(self):
        return {
            "id" : self.id,
            "title" : self.title,
            "is_goal_completed" : self.goal_completed_at is not None
        }

    def goal_task_dict(self):
        return {
            "id" : self.id,
            "title" : self.title,
            "tasks" : [task.task_to_dict_w_goal() for task in self.tasks]
        }
    @classmethod
    def from_dict(cls, values):
        columns = set(cls.COLUMNS)
        filtered = {k:v for k, v in values.items() if k in columns}
        return cls(**filtered)

    def replace_with_dict(self, values):
        for column in self.COLUMNS:
            if column in values:
                setattr(self, column, values[column])
            else:
                return ("ValueError: required column completed_at missing")
