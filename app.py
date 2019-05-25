from flask import Flask, request, make_response, redirect, abort, render_template, url_for, session, flash, json
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from forms.name_form import NameForm
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from threading import Thread

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USER_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASK_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@admin.com>'
app.config['FLASKY_AMDIN'] = os.environ.get('FLASKY_ADMIN')
mail = Mail(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %s' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %s>' % self.username

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

def send_email(to, subject, template, **kwargs):
    message = Message(app.config['FLASK_MAIL_SUBJECT_PREFIX'] + subject,
                      sender=app.config['FLASKY_MAIL_SENER'],
                      recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    thread = Thread(target=send_email, args=[app, message])
    thread.start()
    return thread

def send_async_email(app, message):
    with app.app_context():
        mail.send(message)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True

        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
        # old_name = session.get('name')
        # if old_name is not None and old_name != form.name.data:
        #     flwash('Looks like you have changed your name, {}'.format(form.name.data))
        # session['name'] = form.name.data
        # # return redirect(url_for('index')) # this was triggering exceptions
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           current_time=datetime.utcnow(),
                           known=session.get('known', False),)


@app.route('/user/<name>')
def get_user(name: str):
    return render_template('user.html', name = name)

@app.route('/json-example')
def json_example():
    return app.response_class(
        response=json.dumps({'name': 'My name is cake', 'is_active': True}),
        status=200,
        mimetype='application/json',
    )

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run()
