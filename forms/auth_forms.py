from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError
)

from models.user import User


class RegisterForm(FlaskForm):

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=3, max=100)
        ]
    )

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=4, max=30)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password")
        ]
    )

    submit = SubmitField("Create Account")

    def validate_username(self, username):

        user = User.query.filter_by(
            username=username.data
        ).first()

        if user:
            raise ValidationError(
                "Username already exists."
            )

    def validate_email(self, email):

        user = User.query.filter_by(
            email=email.data
        ).first()

        if user:
            raise ValidationError(
                "Email already registered."
            )


class LoginForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[
            DataRequired()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Login")