from app import db
from flask import Blueprint, jsonify, request
from app.models.goal import Goal
from app.models.task import Task
from functools import wraps
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

def require_task(endpoint):
    @wraps(endpoint)
    def fn(*args, task_id, **kwargs):
        task = Task.query.get(task_id)

        if not task:
            return jsonify(None), 404
        
        return endpoint(*args, task=task, **kwargs)
    return fn

def require_goal(endpoint):
    @wraps(endpoint)
    def fgn(*args, goal_id, **kwargs):
        goal = Goal.query.get(goal_id)

        if not goal:
            return jsonify(None), 404
        
        return endpoint(*args, goal=goal, **kwargs)
    return fgn

@tasks_bp.route("", methods=["GET"])
def get_tasks():
    sort_query = request.args.get("sort")
    if sort_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    elif sort_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    
    else:
        tasks = Task.query.all()
    
    tasks_response = [task.to_dict() for task in tasks]
    return jsonify(tasks_response), 200

@goals_bp.route("", methods=["GET"])
def get_goals():
    goals = Goal.query.all()
    goal_response = [goal.to_dict() for goal in goals]
    return jsonify(goal_response), 200

@goals_bp.route("", methods=["POST"])
def post_goals():
    request_body = request.get_json()

    new_goal = Goal.from_dict(request_body)

    if "title" not in request_body:
        return ({
        "details": "Invalid data"
    }), 400

    db.session.add(new_goal)
    db.session.commit()

    return jsonify({"goal" : new_goal.to_dict()}), 201

@tasks_bp.route("", methods=["POST"])
def post():
    request_body = request.get_json()

    new_task = Task.from_dict(request_body)

    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return ({
        "details": "Invalid data"
    }), 400

    db.session.add(new_task)
    db.session.commit()

    return jsonify({"task" : new_task.to_dict()}), 201

@goals_bp.route("/<goal_id>", methods=["GET"])
@require_goal
def get(goal):  
    return jsonify({"goal": goal.to_dict()}), 200

@tasks_bp.route("/<task_id>", methods=["GET"])
@require_task
def get(task):  
    return jsonify({"task": task.to_dict()}), 200

@goals_bp.route("/<goal_id>", methods=["PUT"])
@require_goal
def put(goal):
    form_data = request.get_json()

    goal.replace_with_dict(form_data)

    db.session.commit()

    return jsonify({"goal": goal.to_dict()}), 200

@tasks_bp.route("/<task_id>", methods=["PUT"])
@require_task
def put(task):
    form_data = request.get_json()

    task.replace_with_dict(form_data)

    db.session.commit()

    return jsonify({"task": task.to_dict()}), 200

@goals_bp.route("/<goal_id>", methods=["DELETE"])
@require_goal
def delete(goal):
    db.session.delete(goal)
    db.session.commit()
    return jsonify ({"details": (f"Goal {goal.id} \"{goal.title}\" successfully deleted")}), 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
@require_task
def delete(task):
    db.session.delete(task)
    db.session.commit()
    return jsonify ({"details": (f"Task {task.id} \"{task.title}\" successfully deleted")}), 200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
@require_task
def complete_patch(task):
    request.get_json()

    task.completed_at = datetime.utcnow()

    db.session.commit()

    load_dotenv()

    data = {"token": os.environ.get("SLACK_TOKEN"), 
                "channel": os.environ.get("CHANNEL_ID"), 
                "text": f"Someone just completed the task {task.title}"}
    url = os.environ.get("SLACK_URL")
    requests.post(url, data)

    return jsonify({"task": task.to_dict()}), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
@require_task
def incomplete_patch(task):
    request.get_json()

    task.completed_at = None

    db.session.commit()

    return jsonify({"task": task.to_dict()}), 200
