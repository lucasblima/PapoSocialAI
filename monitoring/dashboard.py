from flask import Blueprint, render_template, jsonify
from crew import initialize_crew

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/dashboard')
def dashboard():
    return render_template('monitoring/dashboard.html')

@monitoring_bp.route('/api/agent_status')
def agent_status():
    crew = initialize_crew()
    # This is a placeholder. In a real implementation, you would track the status of each agent.
    statuses = {agent.role: "Active" for agent in crew.agents}
    return jsonify(statuses)

@monitoring_bp.route('/api/task_status')
def task_status():
    crew = initialize_crew()
    # This is a placeholder. In a real implementation, you would track the status of each task.
    statuses = {task.description: "In Progress" for task in crew.tasks}
    return jsonify(statuses)
