from flask import Blueprint, redirect, url_for, session
from flask_dance.contrib.github import github
from .models import User
from . import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('main.tasks'))

@auth_bp.route('/login/github')
def login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    resp = github.get('/user')
    profile = resp.json()
    github_id = str(profile['id'])
    user = User.query.filter_by(github_id=github_id).first()
    if not user:
        user = User(github_id=github_id, username=profile['login'])
        db.session.add(user)
        db.session.commit()
    session['user_id'] = user.id
    return redirect(url_for('main.tasks'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
