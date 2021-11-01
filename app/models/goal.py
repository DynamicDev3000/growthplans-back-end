from flask import current_app
from app import db

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)

    COLUMNS = ["title"]
    
    def to_dict(self):
        return {
            "id" : self.id,
            "title" : self.title,
        }

    @classmethod
    def from_dict(cls, values):
        columns = set(cls.COLUMNS)
        filtered = {k:v for k, v in values.items() if k in columns}
        return cls(**filtered)
    #for regular patch
    def update_from_dict(self, values):
        for column in self.COLUMNS:
            if column in values:
                setattr(self, column, values[column])

    def replace_with_dict(self, values):
        for column in self.COLUMNS:
            if column in values:
                setattr(self, column, values[column])
            else:
                return ("ValueError: required column completed_at missing")
