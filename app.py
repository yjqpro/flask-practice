from flask import (
    Flask,
    request,
    abort,
    flash,
    redirect,
    url_for,
    render_template)
from flask_login import (LoginManager, UserMixin, login_user, login_required)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy




app = Flask(__name__)

app.config['SECRET_KEY'] = '12345678'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

db.create_all()


@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User.query.filter_by(username=user_id).one_or_none()


# @login_manager.unauthorized_handler
# def unauthorized():
    # return redirect(url_for('login'))


@app.route('/', methods=['GET'])
def index():
    """
    index
    """
    return "Hello World"


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
        except:
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
    print(form.validate_on_submit())
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one_or_none()
        if user:
            login_user(user)
        else:
            return render_template('login.html', form=form)

        flash('Logged in successfully.')

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
        # return abort(400)

        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)
