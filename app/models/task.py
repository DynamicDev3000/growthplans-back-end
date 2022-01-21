from flask import current_app
from app import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'),nullable=True)

    COLUMNS = ["description", "completed_at"]
    
    def to_dict(self):
        return {
            "id" : self.id,
            "description" : self.description    ,
            "is_complete" : self.completed_at is not None
        }
    def task_to_dict_w_goal(self):      
        return {
            "id" : self.id,
            "goal_id": self.goal_id,
            "description" : self.description,
            "is_complete" : self.completed_at is not None
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
