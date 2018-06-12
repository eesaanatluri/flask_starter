from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from . import auth
from forms import LoginForm, RegistrationForm
from .. import db
from ..models import Employee

from flask_mail import Message
from app import mail

from flask import current_app as app
from threading import Thread

from flask import request

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

        #def send_async_email(msg):
        #    with app.app_context():
        #        mail.send(msg)


        def send_email(subject, recipients, text_body, html_body):
            msg = Message(subject, recipients=recipients)
            msg.body = text_body
            msg.html = html_body
            mail.send(msg)
            #thr = Thread(target=send_async_email, args=[msg])
            #thr.start()
        flash('You have successfully registered! Please check your email to confirm your registration .')

        def send_registration_verification_email(employee):
            token = Employee.get_confirmation_token(employee)
            send_email('Welcome to Research Computing',
               recipients=[employee.email],
               text_body=render_template('auth/registration_verification_email.txt',
                                         user=employee, token=token),
               html_body=render_template('auth/registration_verification_email.html',
                                         user=employee, token=token))

        send_registration_verification_email(employee)

        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')

@auth.route('/confirm', methods=['GET', 'POST'])
def confirm():
    token = request.args.get('token')
    userid = Employee.verify_confirmation_token(token)
    if userid:
        return redirect(url_for('auth.login'))
        flash('Congrats! your account is ready and your token is verified. You can now login.')


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
