from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):

    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Student', 'Student'),
    ]

    student_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Student')
    password_reset_token = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username

class Lab(models.Model):
    room_number = models.IntegerField(unique=True)
    total_seats = models.IntegerField(validators=[MinValueValidator(1)])
    available_seats = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f'Lab {self.room_number}'

class Reservation(models.Model):

    STATUS_CHOICES =[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    seat_number = models.IntegerField()
    reservation_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f'{self.user} - Lab {self.lab}'

