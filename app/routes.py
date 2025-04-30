from flask import Blueprint, render_template, request, redirect, url_for, session
from .models import Task
from . import db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.before_request
def require_login():
    if 'user_id' not in session and request.endpoint not in ('auth.login', 'github.login'):
        return redirect(url_for('auth.login'))

@main_bp.route('/tasks')
def tasks():
    user_id = session['user_id']
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.due_date).all()
    return render_template('tasks.html', tasks=tasks)

@main_bp.route('/tasks/add', methods=['POST'])
def add_task():
    data = request.form
    t = Task(
        title=data['title'],
        description=data['description'],
        due_date=datetime.fromisoformat(data['due_date']),
        priority=int(data['priority']),
        category=data['category'],
        user_id=session['user_id']
    )
    db.session.add(t)
    db.session.commit()
    return redirect(url_for('main.tasks'))

@main_bp.route('/tasks/edit/<int:tid>', methods=['POST'])
def edit_task(tid):
    t = Task.query.get_or_404(tid)
    data = request.form
    t.title = data['title']
    t.description = data['description']
    t.due_date = datetime.fromisoformat(data['due_date'])
    t.priority = int(data['priority'])
    t.category = data['category']
    db.session.commit()
    return redirect(url_for('main.tasks'))

@main_bp.route('/tasks/delete/<int:tid>')
def delete_task(tid):
    t = Task.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    return redirect(url_for('main.tasks'))