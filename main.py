# FLASK Tutorial 1 -- We show the bare bones code to get an app up and running

# imports
import os                 # os is used to get environment variables IP & PORT
import bcrypt
from flask import Flask   # Flask is the web app that we will customize
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from database import db
from models import Task as Task
from models import User as User
from models import Comment as Comment
from forms import RegisterForm, LoginForm, CommentForm

app = Flask(__name__)     # create an app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_task_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SE3155'
#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)
# Setup models

# @app.route is a decorator. It gives the function "index" special powers.
# In this case it makes it so anyone going to "your-url/" makes this function
# get called. What it returns is what is shown as the web page
@app.route('/')
@app.route('/index')
def index():
    if session.get('user'):
        return render_template("index.html", user=session['user'], dark_mode=session['dark_mode'])
    return render_template("index.html")
    

@app.route('/tasks')
def get_tasks():
    if session.get('user'):
        my_tasks = db.session.query(Task).all()
        
        return render_template('tasks.html', tasks=my_tasks, user=session['user'], dark_mode=session['dark_mode'])
    else:
        return redirect(url_for('login'))

@app.route('/tasks/<task_id>')
def get_task(task_id):
    if session.get('user'):

        my_task = db.session.query(Task).filter_by(id=task_id).one()
        form = CommentForm()
        return render_template('task.html', task=my_task, user=session['user'], form=form, dark_mode=session['dark_mode'])
    else:
        return redirect(url_for('login'))

@app.route('/tasks/new', methods=['GET', 'POST'])
def new_task():
    if session.get('user'):
        if request.method == 'POST':
            title = request.form['title']
            text = request.form['taskText']
            from datetime import date
            today = date.today()
            today = today.strftime("%m-%d-%Y")
            new_record = Task(title, text, today, session['user_id'])
            db.session.add(new_record)
            db.session.commit()

            return redirect(url_for('get_tasks'))
        else:
            return render_template('new.html', user=session['user'], dark_mode=session['dark_mode'])
    else:
        return redirect(url_for('login'))

@app.route('/tasks/edit/<task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    if session.get('user'):
        if request.method == 'POST':
            title = request.form['title']
            text = request.form['taskText']
            task = db.session.query(Task).filter_by(id=task_id).one()
            task.title = title
            task.text = text

            db.session.add(task)
            db.session.commit()

            return redirect(url_for('get_tasks'))
        else:
            a_user = db.session.query(User).filter_by(email='jmurph4@uncc.edu').one()

            my_task = db.session.query(Task).filter_by(id=task_id).one()

            return render_template('new.html', task=my_task, user=session['user'], dark_mode=session['dark_mode'])
    else:
        return redirect(url_for('login'))

@app.route('/tasks/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    if session.get('user'):
        my_task = db.session.query(Task).filter_by(id=task_id).one()
        db.session.delete(my_task)
        db.session.commit()
        return redirect(url_for('get_tasks'))
    else:
        return redirect(url_for('login'))

@app.route('/tasks/like/<task_id>', methods=['POST', 'GET'])
def like_task(task_id):
    if session.get('user'):
        my_task = db.session.query(Task).filter_by(id=task_id).one()
        if session[str(my_task.id)]:
            newLikes = my_task.likes - 1
            my_task.likes = newLikes
            session[str(my_task.id)] = False
        else:
            newLikes = my_task.likes + 1
            my_task.likes = newLikes
            session[str(my_task.id)] = True

        db.session.add(my_task)
        db.session.commit()

        return redirect(url_for('get_tasks'))
    else:
        return redirect(url_for('login'))

@app.route('/modechange', methods=['POST', 'GET'])
def change_mode():

    if session.get('user'):
        if session['dark_mode'] == False:
            session['dark_mode'] = True
        else:
            session['dark_mode'] = False

        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        session['dark_mode'] = False
        tasks = db.session.query(Task).all()
        for current_task in tasks:
            session[str(current_task.id)] = False
        # show user dashboard view
        return redirect(url_for('index'))

    # something went wrong - display register view
    return render_template('register.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            session['dark_mode'] = False
            tasks = db.session.query(Task).all()
            for current_task in tasks:
                session[str(current_task.id)] = False

            # render view
            return redirect(url_for('index'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)

@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))

@app.route('/tasks/<task_id>/comment', methods=['POST'])
def new_comment(task_id):
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            new_record = Comment(comment_text, int(task_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('get_task', task_id=task_id))

    else:
        return redirect(url_for('login'))

app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

with app.app_context():
    db.create_all()   # run under the app context


# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000/index

# task that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.