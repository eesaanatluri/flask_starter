from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from . import auth
from forms import LoginForm, RegistrationForm
from .. import db
from ..models import Employee

from flask_mail import Message
from app import mail


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add an employee to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        employee = Employee(email=form.email.data,
                            username=form.username.data,
                            first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            password=form.password.data)

        # add employee to the database
        db.session.add(employee)
        db.session.commit()

        def send_async_email(msg):
            with app.app_context():
            mail.send(msg)


        def send_email(subject, recipients, text_body, html_body):
            msg = Message(subject, recipients=recipients)
            msg.body = text_body
            msg.html = html_body
            thr = Thread(target=send_async_email, args=[msg])
            thr.start()
        flash('You have successfully registered! Please check your email to confirm your registration .')

        def send_registration_verification_email(user):
            token = user.get_confirmation_token()
            send_email('Welcome to Research Computing',
               sender=app.config['ADMINS'][0], #use a real email or set in FLASK_ENV
               recipients=[user.email],
               text_body=render_template('auth/registration_verification_email.txt',
                                         user=user, token=token),
               html_body=render_template('auth/registration_verification_email.html',
                                         user=user, token=token))

        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log an employee in through the login form
    """
    form = LoginForm()
    if form.validate_on_submit():

        # check whether employee exists in the database and whether
        # the password entered matches the password in the database
        employee = Employee.query.filter_by(email=form.email.data).first()
        if employee is not None and employee.verify_password(
                form.password.data):
            # log employee in
            login_user(employee)

            # redirect to the dashboard page after login
            if employee.is_admin:
                return redirect(url_for('home.admin_dashboard'))
            else:
                return redirect(url_for('home.dashboard'))

        # when login details are incorrect
        else:
            flash('Invalid email or password.')

    # load login template
    return render_template('auth/login.html', form=form, title='Login')

@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log an employee out through the logout link
    """
    logout_user()
    flash('You have successfully been logged out.')

    # redirect to the login page
    return redirect(url_for('auth.login'))
