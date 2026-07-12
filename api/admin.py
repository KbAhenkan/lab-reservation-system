from django.contrib import admin
from .models import User, Lab, Reservation

# Register your models here.
admin.site.register(User)
admin.site.register(Lab)
admin.site.register(Reservation)