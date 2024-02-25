from datetime import date

import flask_login
from click import Abort
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager

from typing import List
from sqlalchemy import ForeignKey


# Import your forms from the forms.py
from forms import *

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''
login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

@login_manager.user_loader
def load_user(id):
    user =  db.session.execute(db.select(User).where(User.id==id)).scalar()
    return user




# TODO: Configure Flask-Login
@app.route("/login", methods=["GET", "POST"])
def login():
    print("Iam here")
    login = Login()
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            if check_password_hash(user.password, password):
                print("User check successful")
                print(f"user email {user.email}, password: {user.password}, user ID: {user.id}")
                login_user(user, remember=True)
                print("Completed Login")
                return redirect(url_for('get_all_posts'))
            else:
                return render_template("login.html", form=login)
    else:
        print("I am at get")
        return render_template("login.html", form=login)

# CREATE DATABASEaf
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    author_id: Mapped[int]  = mapped_column(ForeignKey("user.id"))
    parent: Mapped["User"] = relationship(back_populates="children")


# TODO: Create a User table for all your registered users. 
class User(db.Model, UserMixin):
    __tablename__ = "user"
    email = mapped_column(String(250))
    password = mapped_column(String(250))
    name = mapped_column(String(250))
    id = mapped_column(Integer, unique=True, primary_key=True)
    children: Mapped[List["BlogPost"]] = relationship(back_populates="parent")

with app.app_context():
    db.create_all()


# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        new_user = User()
        new_user.email = request.form["email"]
        new_user.password = request.form["password"]
        new_user.name = request.form["name"]
        new_user.password = generate_password_hash(new_user.password, method="pbkdf2:sha256", salt_length=8)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    else:
        flash("User Creation Failed")
        return render_template("register.html", form= form)
    return render_template("register.html", form= form)


# TODO: Retrieve a user from the database based on their email. 




@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    print("UnAuthorized")
    return redirect(url_for('login'))

def admin_only(function_name):
    def secured_posts(*args, **kwargs):
        user_id = flask_login.current_user
        id= user_id.get_id()


        if id == "1":
            return function_name(*args, **kwargs)
        else:
             return abort(403)

    return secured_posts



@app.route('/')
@login_required
def get_all_posts():
    print("get_all_posts")
    user = flask_login.current_user
    id = user.id
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, id= id)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreatePostForm()
    user = current_user
    user_id = user.get_id()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=user.name,
            date=date.today().strftime("%B %d, %Y"),
            author_id= user_id
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post

@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
