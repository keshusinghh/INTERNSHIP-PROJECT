from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

# Prevent caching of dynamic pages to avoid forward/back showing protected pages
@app.after_request
def add_no_cache_headers(response):
    # Skip static assets to allow normal caching
    if request.path.startswith('/static/'):
        return response
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Models
class User(db.Model):
    __tablename__ = 'users'  # Explicitly set table name to 'users' instead of default 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Task', backref='owner', lazy=True)
    sent_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.receiver_id', backref='receiver', lazy=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='to_do')  # to_do, in_progress, done
    # Comment out priority column temporarily to avoid errors
    # priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_visible = db.Column(db.Boolean, default=True)  # Make tasks visible to team by default
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add property to handle missing priority column
    @property
    def priority(self):
        return 'medium'

    @priority.setter
    def priority(self, value):
        # No-op setter to avoid errors when forms submit priority
        pass

class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # added, deleted, modified
    task_id = db.Column(db.Integer, nullable=True)
    task_title = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='activities')

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for team-wide messages
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        user_exists = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()
        if user_exists:
            flash('Username or email already exists')
            return redirect(url_for('register'))
        
        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check for admin login
        if username == 'admin' and password == 'team3':
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                hashed_password = generate_password_hash('team3', method='pbkdf2:sha256')
                admin = User(username='admin', email='admin@nexusboard.com', password=hashed_password, is_admin=True)
                db.session.add(admin)
                db.session.commit()
            
            session['user_id'] = admin.id
            session['username'] = admin.username
            session['email'] = admin.email
            session['is_admin'] = True
            flash('Admin login successful!')
            return redirect(url_for('admin_dashboard'))
        
        # Regular user login
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            session['is_admin'] = user.is_admin
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            # Redirect to avoid POST resubmission when navigating back
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('index'))

# Admin dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin', False):
        flash('Admin access required')
        return redirect(url_for('login'))
    
    users = User.query.filter(User.is_admin == False).all()
    activities = UserActivity.query.order_by(UserActivity.timestamp.desc()).all()
    
    return render_template('admin_dashboard.html', users=users, activities=activities)

# Team chat routes
@app.route('/team_chat')
def team_chat():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    users = User.query.all()
    messages = ChatMessage.query.order_by(ChatMessage.timestamp).all()
    
    return render_template('team_chat.html', users=users, messages=messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    message_text = data.get('message')
    receiver_id = data.get('receiver_id')
    
    if not message_text:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    new_message = ChatMessage(
        sender_id=session['user_id'],
        receiver_id=receiver_id if receiver_id else None,
        message=message_text
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({
        'id': new_message.id,
        'sender': session['username'],
        'sender_id': session['user_id'],
        'message': message_text,
        'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/edit_message/<int:message_id>', methods=['PUT'])
def edit_message(message_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    new_message_text = data.get('message')
    
    if not new_message_text:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    message = ChatMessage.query.get_or_404(message_id)
    
    # Check if the message belongs to the logged-in user
    if message.sender_id != session['user_id']:
        return jsonify({'error': 'You are not authorized to edit this message'}), 403
    
    message.message = new_message_text
    db.session.commit()
    
    return jsonify({
        'id': message.id,
        'message': new_message_text,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/delete_message/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    message = ChatMessage.query.get_or_404(message_id)
    
    # Check if the message belongs to the logged-in user
    if message.sender_id != session['user_id']:
        return jsonify({'error': 'You are not authorized to delete this message'}), 403
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Get current user
    user = User.query.get(session['user_id'])
    
    # Verify current password
    if not check_password_hash(user.password, current_password):
        flash('Current password is incorrect')
        return redirect(url_for('dashboard'))
    
    # Check if new passwords match
    if new_password != confirm_password:
        flash('New passwords do not match')
        return redirect(url_for('dashboard'))
    
    # Update password
    user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.commit()
    
    flash('Password updated successfully')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    to_do_tasks = Task.query.filter_by(user_id=user_id, status='to_do').all()
    in_progress_tasks = Task.query.filter_by(user_id=user_id, status='in_progress').all()
    done_tasks = Task.query.filter_by(user_id=user_id, status='done').all()
    
    # Get team tasks (tasks from other users that are marked as team_visible)
    team_tasks = Task.query.filter(Task.user_id != user_id, Task.team_visible == True).order_by(Task.updated_at.desc()).all()
    
    # Get all users for the team progress section
    team_members = User.query.all()
    
    return render_template('dashboard.html', 
                          to_do_tasks=to_do_tasks, 
                          in_progress_tasks=in_progress_tasks, 
                          done_tasks=done_tasks,
                          team_tasks=team_tasks,
                          team_members=team_members)

# Standalone Task Management page
@app.route('/task_management')
def task_management():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))

    user_id = session['user_id']
    to_do_tasks = Task.query.filter_by(user_id=user_id, status='to_do').all()
    in_progress_tasks = Task.query.filter_by(user_id=user_id, status='in_progress').all()
    done_tasks = Task.query.filter_by(user_id=user_id, status='done').all()

    return render_template('task_management.html',
                           to_do_tasks=to_do_tasks,
                           in_progress_tasks=in_progress_tasks,
                           done_tasks=done_tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status')
    
    new_task = Task(title=title, description=description, status=status, user_id=session['user_id'])
    db.session.add(new_task)
    db.session.commit()
    
    # Log activity
    activity = UserActivity(
        user_id=session['user_id'],
        activity_type='added',
        task_id=new_task.id,
        task_title=title
    )
    db.session.add(activity)
    db.session.commit()
    
    flash('Task added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    task = Task.query.get_or_404(task_id)
    
    # Check if the task belongs to the logged-in user
    if task.user_id != session['user_id']:
        flash('You are not authorized to edit this task')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.status = request.form.get('status')
        task.priority = request.form.get('priority', 'medium')
        
        db.session.commit()
        
        # Log activity
        activity = UserActivity(
            user_id=session['user_id'],
            activity_type='modified',
            task_id=task.id,
            task_title=task.title
        )
        db.session.add(activity)
        db.session.commit()
        
        flash('Task updated successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_task.html', task=task)

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    task = Task.query.get_or_404(task_id)
    
    # Check if the task belongs to the logged-in user
    if task.user_id != session['user_id']:
        flash('You are not authorized to delete this task')
        return redirect(url_for('dashboard'))
    
    task_title = task.title
    db.session.delete(task)
    db.session.commit()
    
    # Log activity
    activity = UserActivity(
        user_id=session['user_id'],
        activity_type='deleted',
        task_title=task_title
    )
    db.session.add(activity)
    db.session.commit()
    
    flash('Task deleted successfully!')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)