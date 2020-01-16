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


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class User(UserMixin):

    def __init__(self, id):
        self._id = id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id


app = Flask(__name__)

app.config['SECRET_KEY'] = '12345678'


login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User(id=user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        user = User(form.username.data)
        login_user(user)

        flash('Logged in successfully.')

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
        # return abort(400)

        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)
