from django.core.exceptions import ValidationError

from messengers.models import User


def email_exist_validator(mail):
    """Validator that checks if email is already in use"""
    mail = User.objects.filter(email=mail)
    if mail.exists():
        raise ValidationError("Email has been used")


def email_not_exist_validator(mail):
    """Validator that checks if email is not already in use"""
    mail = User.objects.filter(email=mail)
    if not mail.exists():
        raise ValidationError(f"There is no account with this email")
