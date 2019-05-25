from datetime import datetime
from flask import render_template, session, redirect, url_for
from . import main
from forms.name_form import NameForm
from flask_login import login_required

from .. import db
from ..models import User

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
        #     session.add(user)
        #     # db.session.commit()
        #     # session['known'] = False
        #     # if app.config['FLASKY_ADMIN']:
        #     #     send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        # # else:
        #     # session['known'] = True
        #
        session['name'] = form.name.data
        form.name.data = ''
        print('validate_on_submit_was_called, will redirect to index')
        return redirect(url_for('.index'))
    print('Will re-render template index.html')
    return render_template('index.html', form=form, name=session.get('name'),
                           known = session.get('known', False),
                           current_time = datetime.utcnow())


@main.route('/secret')
@login_required
def secrete():
    return "Only authenticated users are allowed"