from werkzeug.security import generate_password_hash, check_password_hash

import os

from flask import Flask, render_template, request, flash, abort, redirect, session, g, url_for
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm
from models import db, connect_db, User, ToDo

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///todo'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

with app.test_request_context():    
    connect_db(app)
    db.create_all()


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have successfully logged out.", 'success')
    return redirect("/login")


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """
    if g.user:
        return render_template('/users/home.html')
    else:
        return render_template('/users/home-anon.html')

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404

#########################
#Route to main ToDo list page
@app.route('/todo/list', methods=['GET', 'POST'])
def todo_list():
    if not g.user:
        flash("Please log in to access this page.", "danger")
        return redirect("/login")
    todos = ToDo.query.filter_by(user_id=g.user.id).order_by(ToDo.order).all()
    if request.method == 'POST':
        action = request.form['action']
        todo_id = request.form['todo_id']
        todo = ToDo.query.filter_by(id=todo_id, user_id=g.user.id).first()
        if action == 'delete':
            db.session.delete(todo)
            db.session.commit()
            flash('Todo item deleted successfully!', 'success')
        elif action == 'update':
            name = request.form['name']
            description = request.form['description']
            due_date = request.form['due_date']
            status = request.form['status']
            order = request.form['order']
            todo.name = name
            todo.description = description
            todo.due_date = due_date
            todo.status = status
            todo.order = order
            db.session.commit()
            flash('Todo item updated successfully!', 'success')
        elif action == 'move_up':
            prev_todo = ToDo.query.filter_by(order=int(todo.order)-1).first()
            prev_todo.order = int(todo.order)
            todo.order = int(todo.order)-1
            db.session.commit()
            flash('Todo item moved up successfully!', 'success')
        elif action == 'move_down':
            next_todo = ToDo.query.filter_by(order=int(todo.order)+1).first()
            next_todo.order = int(todo.order)
            todo.order = int(todo.order)+1
            db.session.commit()
            flash('Todo item moved down successfully!', 'success')
        return redirect(url_for('todo_list'))
    return render_template('users/todo_list.html', todos=todos)

# Add ToDo
@app.route('/todo/create', methods=['GET', 'POST'])
def create_todo():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        due_date = request.form['due_date']
        status = request.form['status']
        order = request.form['order']
        todo = ToDo(name=name, description=description, due_date=due_date, status=status, order=order, user_id=g.user.id)
        db.session.add(todo)
        db.session.commit()
        flash('New todo item created successfully!', 'success')
        return redirect(url_for('todo_list'))
    return render_template('users/create_todo.html')
