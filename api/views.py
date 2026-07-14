from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import User, Lab, Reservation
from .serializers import UserSerializer, LabSerializer, ReservationSerializer
from django.db.models import Sum
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import BasePermission, IsAuthenticated
import secrets
from django.core.mail import send_mail

# ----------------------PASSWORD CHANGE FUNCTIONS---------------------------
@api_view(['POST'])
def password_reset_request(request):
    email = request.data.get('email')
    print(f'Email received: {email}')  # add this
    
    try:
        user = User.objects.get(email=email)
        print(f'User found: {user}')  # add this
    except User.DoesNotExist:
        print('User not found!')  # add this
        return Response({'status': 'OK'})
    
    token = secrets.token_urlsafe(30)
    print(f'Token generated: {token}')  # add this
    user.password_reset_token = token
    user.save()
    print('Token saved!')  # add this
    
    try:
        send_mail(
            'Password Reset Request',
            f'Hello,\n\nYou requested a password reset for your LabReserve account.\n\nClick the link below to reset your password:\n\nhttp://localhost:5173/reset-password?token={token}\n\nIf you did not request this, please ignore this email.',
            'ahenkankwabena2@gmail.com',
            [email],
        )
        print('Email sent successfully!')
    except Exception as e:
        print(f'Email error: {e}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({'status': 'OK'})


@api_view(['POST'])
def password_reset_confirm(request):
    token = request.data.get('token')
    password = request.data.get('password')
    
    try:
        user = User.objects.get(password_reset_token=token)
    except User.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Set new password
    user.set_password(password)
    user.password_reset_token = None  # clear the token after use
    user.save()
    
    return Response({'message': 'Password reset successfully'})


# ----------------------PERMISSION CHECKER FUNCTIONS---------------------------

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin'
    
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Student'
    
# ----------------------SIGNUP FUNCTION---------------------------
@api_view(['POST'])
def signup(request):
    data = request.data

    if data['password']  != data['confirm_password']:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(
        username=data['email'],
        email=data['email'], 
        password=data['password'],
        first_name=data['full_name'], 
        role=data.get('role', 'Student'),

Fix it by adding student_id:
pythonuser = User.objects.create_user(
    username=data['email'],
    email=data['email'], 
    password=data['password'],
    first_name=data['full_name'], 
    role=data.get('role', 'Student'),
    student_id=data.get('student_id', None)
    )
   
    return Response({
        'message': 'Account created successfully',
        'user': {
            'id': user.id,
            'full_name': user.first_name,
            'email': user.email,
            'role': user.role
        }
    }, status=status.HTTP_201_CREATED)

# ----------------------LOGIN FUNCTION---------------------------
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    user = authenticate(username=user.username, password=password)
    if user is None:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)

    return Response({
        'message': 'Login successful',
        'token': str(refresh.access_token),
        'user': {
            'id': user.id,
            'full_name': user.first_name,
            'email': user.email,
            'role': user.role
        }
    })

# ----------------------DASHBOARD FUNCTION---------------------------
@api_view(['GET'])
@permission_classes([IsAdmin])
def dashboard(request):
    total_labs = Lab.objects.count()
    total_users = User.objects.count()
    active_reservations = Reservation.objects.filter(status='Confirmed').count()
    total_seats_available = Lab.objects.aggregate(Sum('available_seats'))['available_seats__sum']

    return Response({
        'total_labs': total_labs,
        'total_users': total_users,
        'active_reservations': active_reservations,
        'total_available_seats': total_seats_available
    })
# ----------------------USER FUNCTIONS---------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAdmin])
def user_list(request):
    if request.method == 'GET':
        users =  User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdmin])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':    
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# ------------------------LAB FUNCTIONS-----------------------------
@api_view(['GET', 'POST']) # GET for showing all labs and POST for creating lab
def lab_list(request):
    if request.method == 'GET':
        labs = Lab.objects.all()
        serializer = LabSerializer(labs, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        if not IsAdmin().has_permission(request, None):
            return Response({'error': 'Only admins can add labs'}, status=status.HTTP_403_FORBIDDEN)
        serializer = LabSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdmin])
def lab_detail(request, pk):
    try:
        lab = Lab.objects.get(pk=pk)
    except Lab.DoesNotExist:
        return Response({'error': 'This lab does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = LabSerializer(lab, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        lab.delete()
        return Response({'message': 'Lab deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

# ----------------------RESERVATION FUNCTIONS---------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def reservation_list(request):
    if request.method == 'GET':
        reservations = Reservation.objects.all()
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)
        
    if request.method == 'POST':
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():

            lab = Lab.objects.get(pk=request.data['lab'])
            
            if lab.available_seats <= 0:
                return Response({'error': 'No available seats in in this lab'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = request.data['user']
            already_booked = Reservation.objects.filter(user=user, lab=lab).exists()
            if already_booked:
                return Response({'error': 'User already has a reservation in this lab'}, status=status.HTTP_400_BAD_REQUEST)
            
            last_seat = Reservation.objects.filter(lab=lab).count()
            next_seat = last_seat + 1

            serializer.save(seat_number=next_seat)
            lab.available_seats -= 1
            lab.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def reservation_detail(request, pk):
    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = ReservationSerializer(reservation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        lab = reservation.lab
        reservation.delete()

        lab.available_seats += 1
        lab.save()

        return Response({'message': 'Reservation cancelled successfully'}, status=status.HTTP_204_NO_CONTENT)
