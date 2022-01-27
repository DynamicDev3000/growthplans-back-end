from app import db
from flask import Blueprint, jsonify, request, render_template

from app.models.goal import Goal
from app.models.task import Task
from app.models.user import User
from functools import wraps
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")
# users_bp = Blueprint("users", __name__, url_prefix="/users")

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

# @users_bp.route("/", methods=["GET", "POST"])
# def registration():
    

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
    sort_filter = request.args.get("sort")
    if sort_filter == "desc":
        goal_query = Goal.query.order_by(Goal.due_date.desc())
    elif sort_filter == "asc":
        goal_query = Goal.query.order_by(Goal.due_date.asc())
    else:
        goal_query = Goal.query

#localhost:5000/goals?is_goal_completed=true
    completed_filter = request.args.get("is_goal_completed")
    if completed_filter == "true":
        goal_query = goal_query.filter(Goal.goal_completed_at.isnot(None)) 
    
    return goal_query.all()

#get goals completed = true

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

#patch request to edit goals - works tested
@goals_bp.route("/<goal_id>", methods=["PATCH"])
@require_goal
def patch_goal(goal):
    request_body = request.get_json()

    goal.title = request_body["title"]

    db.session.commit()

    return jsonify({"updated title": goal.title}), 200

#patch request to edit subtasks
#works tested with request in this format
# {   "description" : "Youtube 3"
# }
@goals_bp.route("/<goal_id>/<task_id>", methods=["PATCH"])
@require_goal
@require_task
def patch_task(goal, task):
    request_body = request.get_json()

    task.description = request_body["description"]

    db.session.commit()

    return jsonify({"updated description": task.description}), 200

@goals_bp.route("/<goal_id>/<task_id>/mark_complete", methods=["PATCH"])
@require_goal
@require_task
def complete_patch(task, goal):
    request.get_json()

    task.completed_at = datetime.utcnow()
    
    #check if all tasks are completed for that goal and if true complete goal
    if all(task.completed_at for task in goal.tasks):
        goal.goal_completed_at = datetime.utcnow()

    db.session.commit()

    return jsonify({"task": task.to_dict()}), 200

@goals_bp.route("/<goal_id>/<task_id>/mark_incomplete", methods=["PATCH"])
@require_goal
@require_task
def incomplete_patch(task, goal):
    request.get_json()

    task.completed_at = None

    db.session.commit()

    return jsonify({"task": task.to_dict()}), 200

#delete tasks under goal
#works tested
@goals_bp.route("/<goal_id>/<task_id>", methods=["DELETE"])
@require_goal
@require_task
def delete_task_w_goal(goal, task):
    db.session.delete(task)
    db.session.commit()
    return jsonify ({"details": (f"Task {task.description} successfully deleted")}), 200

#works tested
@goals_bp.route("/<goal_id>", methods=["DELETE"])
@require_goal
def delete(goal):
    db.session.delete(goal)
    db.session.commit()
    return jsonify ({"details": (f"Goal {goal.title} successfully deleted")}), 200