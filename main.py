from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, blog_title, body):
        self.blog_title = blog_title
        self.body = body


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('base.html')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'GET':
        blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog", blogs=blogs)
    

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html', title="Add a Blog Entry")
    else:
        blog_title = request.form['blog_title']
        body = request.form['body']
        new_blog = Blog(blog_title, body)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/single')


@app.route('/single', methods=['GET'])
def single():
    
    return render_template('single.html', title={{blog_title}})


if __name__ == '__main__':
    app.run()