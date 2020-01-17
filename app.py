import os
from random import choice
import string
import time
from io import BytesIO
from datetime import timedelta
from flask import (
    Flask,
    request,
    abort,
    flash,
    redirect,
    url_for,
    session,
    render_template,
    send_file
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    current_user)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_session import Session
from extensions import db, admin, login_manager
from models import User
from admin_view import FooAdminIndexView, AuthenticationModelView
import captcha_util


app = Flask(__name__)

# app.config['SECRET_KEY'] = os.urandom(24)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my.db'
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
Session(app)


def init_extensions(app):
    db.init_app(app)
    admin.init_app(app, index_view=FooAdminIndexView())
    admin.add_view(AuthenticationModelView(User, db.session))
    login_manager.init_app(app)
    login_manager.login_view = 'login'


init_extensions(app)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User.query.get(user_id)


@app.route('/', methods=['GET'])
def index():
    """
    index
    """
    # return f"Hello World: {session['uid']}"
    return f"Hello World"


@app.route('/test', methods=['GET'])
@login_required
def test():
    """
    test
    """
    return 'test'


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        login_user(user)

        try:
            db.session.add(user)
            db.session.commit()
        except BaseException:
            db.session.rollback()

        flash('Register in successfully.')

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
        # return abort(400)

        return redirect(next or url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one_or_none()
        if user:
            login_user(user)
        else:
            return render_template('login.html', form=form)

        flash('Logged in successfully.')
        session['uid'] = form.username.data

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
        # return abort(400)

        print(next)
        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)


@app.route('/initdb', methods=['GET'])
def init_db():
    db.create_all()
    return 'init db'


@app.route('/set-session', methods=['GET'])
def set_session():
    session['urandom'] = os.urandom(24)
    return 'ok'


@app.route('/get-session', methods=['GET'])
def get_session():
    return session['urandom']


@app.route('/verify-code', methods=['GET'])
def verify_code():
    # chars = string.ascii_letters + string.digits
    # verify_code = ''.join([choice(chars) for i in range(4)])
    # session['register_verify_code'] = verify_code
    # session['register_verify_code_expiry_time'] = int(
        # time.time()) + timedelta(minutes=3).total_seconds()
    # return verify_code
    img, verify_code = captcha_util.create_validate_code()
    session['register_verify_code'] = verify_code
    session['register_verify_code_expiry_time'] = int(
        time.time()) + timedelta(minutes=3).total_seconds()
    image_binary = BytesIO()
    img.save(image_binary, format='JPEG')
    image_binary.seek(0, 0)
    return send_file(
        image_binary,
        mimetype='image/jpeg',
        as_attachment=True,
        attachment_filename="verify_code.jpg")


@app.route('/check-verify-code', methods=['GET'])
def check_verify_code():
    pass
