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

#create goal, tasks and attaches them to goal
@goals_bp.route("", methods=["POST"])
def post_tasked_goals():
    request_body = request.get_json()

    new_goal = Goal.from_dict(request_body["goal"])

    if "title" not in request_body["goal"]:
        return ({
        "details": "Invalid data"
    }), 400

    db.session.add(new_goal)

    if "tasks" not in request_body:
        return ({
        "details": "Invalid data"
    }), 400

    new_tasks = []
    for task in request_body["tasks"]:
        new_task = Task.from_dict(task)
        new_tasks.append(new_task)
    
    new_goal.tasks = new_tasks

    db.session.add_all(new_tasks)
    db.session.commit()

    new_response = {
    "id": new_goal.id,
    "title": new_goal.title,
    "tasks": [task.task_to_dict_w_goal() for task in new_goal.tasks]
    }

    return jsonify(new_response), 200

def sort_filter_goals():
    sort_query = request.args.get("sort")
    if sort_query == "desc":
        goals = Goal.query.order_by(Goal.due_date.desc())
    elif sort_query == "asc":
        goals = Goal.query.order_by(Goal.due_date.asc())
    else:
        goals = Goal.query.all()

    filter_query = request.args.get("due_date")
    if filter_query:
        goals = Goal.query.filter(Goal.due_date.contains(filter_query))
    
    return goals
#tested - works
@goals_bp.route("", methods=["GET"])
def get_goals():
    goals = sort_filter_goals()

    goal_response = [goal.to_dict() for goal in goals]

    return jsonify(goal_response), 200

#tested - works
@goals_bp.route("/<goal_id>", methods=["GET"])
@require_goal
def get(goal):  
    return jsonify({"goal": goal.to_dict()}), 200

#tested - works
@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
@require_goal
def get_tasked_goal(goal):
    return jsonify(goal.goal_task_dict()), 200

#patch request to edit subtasks
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

    task.completed_at = datetime.date()

    db.session.commit()

    return jsonify({"task": task.to_dict()}), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
@require_task
def incomplete_patch(task):
    request.get_json()

    task.completed_at = None

    db.session.commit()

    return jsonify({"task": task.to_dict()}), 200
