"""
Views for authentication and user management.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from .models import User, AccessLog, PasswordHistory, UserSession
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    PasswordChangeSerializer
)
import logging

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Log registration
        AccessLog.objects.create(
            user=user,
            access_type='login_success',
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'action': 'user_registration'}
        )
        
        logger.info(f"New user registered: {user.username}")
        
        return Response(
            {'message': 'Registration successful. Please wait for account verification.'},
            status=status.HTTP_201_CREATED
        )
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoginView(APIView):
    """
    User login endpoint with security logging.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            
            # Reset failed login attempts
            user.failed_login_attempts = 0
            user.last_login_ip = ip_address
            user.save()
            
            # Create user session
            login(request, user)
            
            # Create session record
            UserSession.objects.create(
                user=user,
                session_key=request.session.session_key,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Log successful login
            AccessLog.objects.create(
                user=user,
                access_type='login_success',
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            logger.info(f"User logged in: {user.username} from {ip_address}")
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user, context={'request': request}).data
            })
            
        except Exception as e:
            # Log failed login attempt
            username = request.data.get('username', 'unknown')
            
            # Increment failed attempts for existing users
            try:
                user = User.objects.get(username=username)
                user.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
                    
                    AccessLog.objects.create(
                        user=user,
                        access_type='account_locked',
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={'reason': 'too_many_failed_attempts'}
                    )
                
                user.save()
                
                AccessLog.objects.create(
                    user=user,
                    access_type='login_failed',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={'username': username}
                )
                
            except User.DoesNotExist:
                # Log failed attempt for non-existent user
                AccessLog.objects.create(
                    access_type='login_failed',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={'username': username, 'reason': 'user_not_found'}
                )
            
            security_logger.warning(f"Failed login attempt for {username} from {ip_address}")
            
            raise e
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(APIView):
    """
    User logout endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Deactivate user session
        try:
            user_session = UserSession.objects.get(
                user=request.user,
                session_key=request.session.session_key,
                is_active=True
            )
            user_session.is_active = False
            user_session.logout_at = timezone.now()
            user_session.save()
        except UserSession.DoesNotExist:
            pass
        
        # Log logout
        AccessLog.objects.create(
            user=request.user,
            access_type='logout',
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f"User logged out: {request.user.username}")
        
        logout(request)
        return Response({'message': 'Logout successful'})
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view and update.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    """
    Password change endpoint with history tracking.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        new_password = serializer.validated_data['new_password']
        
        # Save old password to history
        PasswordHistory.objects.create(
            user=user,
            password_hash=user.password
        )
        
        # Set new password
        user.set_password(new_password)
        user.password_changed_at = timezone.now()
        user.save()
        
        # Log password change
        AccessLog.objects.create(
            user=user,
            access_type='password_change',
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f"Password changed for user: {user.username}")
        
        return Response({'message': 'Password changed successfully'})
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions(request):
    """
    Get user permissions and capabilities.
    """
    user = request.user
    
    permissions_data = {
        'role': user.role,
        'is_healthcare_provider': user.is_healthcare_provider,
        'can_access_patient_data': user.can_access_patient_data,
        'can_modify_medical_records': user.can_modify_medical_records,
        'organization': user.organization.name if user.organization else None,
    }
    
    return Response(permissions_data)