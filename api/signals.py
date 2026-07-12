from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    print('Signal fired!')
    print(f'Token: {reset_password_token.key}')
    send_mail(
        'Password Reset Request',
        f'Hello,\n\nYour reset token is:\n\n{reset_password_token.key}\n\nUse this to reset your password.',
        'ahenkankwabena2@gmail.com',
        [reset_password_token.user.email],
    )