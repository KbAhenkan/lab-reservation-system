from rest_framework import serializers
from .models import User, Lab, Reservation
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username','first_name', 'last_name', 'student_id', 'email', 'role', 'is_active', 'status']
        extra_kwargs = {
            'password': {'write_only':True}
        }
    
    def get_status(self, obj):
        if obj.is_active:
            return 'Active'
        else:
            return 'Inactive'
        
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))

class LabSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    class Meta:
        model = Lab
        fields = ['id', 'room_number', 'total_seats', 'available_seats', 'status']

    def get_status(self, obj):
        if obj.available_seats == 0:
            return 'Full'
        elif obj.available_seats <= obj.total_seats * 0.2:
            return 'Almost Full'
        else:
            return 'Open'

class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    lab = serializers.StringRelatedField()
    reservation_date = serializers.DateTimeField(format="%B %d, %Y", read_only=True)
    reservation_time = serializers.SerializerMethodField()
    seat_number = serializers.IntegerField(read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'user', 'lab', 'seat_number', 'reservation_date', 'reservation_time', 'status']

    def get_reservation_time(self, obj):
        return obj.reservation_date.strftime("%I:%M %p")