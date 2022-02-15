from flask import current_app, jsonify
from app import db
from datetime import datetime 

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    due_date = db.Column(db.DateTime, nullable=True)
    why = db.Column(db.String, nullable=True)
##big why reflection? #foreen obstacles, tools to overcome them
    difficulty = db.Column(db.Float, nullable=True)
    tasks = db.relationship("Task", backref="goal", lazy=True)
    goal_completed_at = db.Column(db.DateTime)

    COLUMNS = ["title", "due_date", "why", "difficulty"]
    
    def to_dict(self):
        return {
            "id" : self.id,
            "title" : self.title,
            "due_date" : self.due_date,
            "why" : self.why,
            "difficulty" : self.difficulty,
            "days_left" : (datetime.now() - self.due_date).days,
            "is_goal_completed" : self.goal_completed_at is not None
        }

    def goal_task_dict(self):
        return {
            "id" : self.id,
            "title" : self.title,
            "due_date" : self.due_date,
            "why" : self.why,
            "difficulty" : self.difficulty,
            "is_goal_completed" : self.goal_completed_at is not None,
            "days_left" : (datetime.now() - self.due_date).days,
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
