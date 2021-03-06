from flask import Flask, request, redirect, render_template, url_for, make_response, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'C@t!c0rn$R@m@z!ng'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, blog_title, body, owner):
        self.blog_title = blog_title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/blog?user=<username>', methods=['POST', 'GET'])
def singleUser(username):
    users = User.query.all()
    username = request.args.get('username')
    # if user in users:
    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)
    body = blog.body
    blog_title = blog.blog_title
    user_id = request.args.get('id')
    user = User.query.get(username)
    return render_template('singleUser.html', blog_title=blog_title, body=body, user_id=user_id, user=user, username=username)


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'GET':
        if request.args.get('id'):
            blog_id = request.args.get('id')
            blog = Blog.query.get(blog_id)
            body = blog.body
            blog_title = blog.blog_title
            return render_template('singleUser.html', blog_title=blog_title, body=body)
        else:
            blogs = Blog.query.all()
            return render_template('blog.html', title="blog users!", blogs=blogs)
    

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html', title="Add a Blog Entry")
    else:
        blog_title = request.form['blog_title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(blog_title, body, owner)
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('blog', id=new_blog.id))


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(password) < 3:
            flash("Invalid password. Must be more than 3 characters.", 'error')
            return redirect('/login')

        if len(username) < 3:
            flash("Invalid username. Must be more than 3 characters", 'error')

        for char in password:
            if char == ' ':
                flash("The password field cannot include spaces", 'error')
                return redirect('/login')

        if password != verify:
            flash("Passwords do not match", 'error')
            return redirect('/login')  

        if username == '' or password == '' or verify == '':
            flash("One or more fields are invalid", 'error')
            return redirect('/login')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash("Username already exists", 'error')
            return redirect('/login')
    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                session['username'] = username
                return redirect('/newpost')
            else:
                flash("Invalid password", 'error')
                return redirect('/login')
        else:
            flash("Username does not exist", 'error')
            return redirect('/login')
    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog.html')


if __name__ == '__main__':
    app.run()