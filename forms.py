from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, IntegerField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    email = EmailField(u'Email')
    password = PasswordField(u'Passsword')
    name = StringField(u'Name')
    submit = SubmitField('Register')
# TODO: Create a LoginForm to login existing users
class Login(FlaskForm):
    email = EmailField(u'Email')
    password = PasswordField(u'Passsword')
    id = IntegerField(u'ID')
    login = SubmitField('Login')
# TODO: Create a CommentForm so users can leave comments below posts
