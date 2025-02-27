from channels.middleware import BaseMiddleware
from django.utils.module_loading import import_string
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.conf import settings
import requests
import logging
import json

logger = logging.getLogger(__name__)
User = get_user_model()


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def verify_user_with_auth_service(self, token):
        try:
            # Verify token with auth service
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(
                f"{settings.USER_SERVICE_URL}/api/user/verify/", 
                headers=headers
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return user_data
            return None
        except Exception as e:
            logger.error(f"Error verifying user with auth service: {e}")
            return None

    def __call__(self, request):
        if not request.path.startswith('/api/chat/'):
            return self.get_response(request)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'detail': 'No token provided'}, status=401)

        try:
            token = auth_header.split(' ')[1]
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            # Verify user with auth service
            user_data = self.verify_user_with_auth_service(token)
            if not user_data:
                return JsonResponse({
                    'detail': 'User verification failed',
                    'code': 'verification_failed'
                }, status=401)

            # Create or get user in chat service
            user, created = User.objects.get_or_create(
                id=user_id,
                defaults={
                    'username': user_data.get('username', f'user_{user_id}'),
                    'email': user_data.get('email', '')
                }
            )

            request.user = user
            request.user_id = user_id
            return self.get_response(request)

        except (InvalidToken, TokenError) as e:
            logger.error(f'Invalid token: {str(e)}')
            return JsonResponse({'detail': 'Invalid token'}, status=401)
        except Exception as e:
            logger.error(f'Authentication error: {str(e)}')
            return JsonResponse({'detail': 'Authentication failed'}, status=401)
        
class TokenAuthMiddleware(BaseMiddleware):
    @database_sync_to_async
    def get_or_create_user(self, user_id, token):
        try:
            # First try to get existing user
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

            # Verify with auth service
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(
                f"{settings.USER_SERVICE_URL}/api/user/verify/",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                user_data = response.json()
                try:
                    # Use get_or_create to handle race conditions
                    user, created = User.objects.get_or_create(
                        id=user_id,
                        defaults={
                            'username': user_data.get('username', f'user_{user_id}'),
                            'email': user_data.get('email', ''),
                            'is_active': True
                        }
                    )
                    if created:
                        user.set_unusable_password()
                        user.save()
                        logger.info(f"Created new user {user_id}")
                    return user
                except Exception as e:
                    logger.error(f"Error creating user: {str(e)}")
                    return None
            
            logger.error(f"Auth service returned {response.status_code}: {response.text}")
            return None

        except Exception as e:
            logger.error(f"Error in get_or_create_user: {str(e)}")
            return None

    async def close_connection(self, send, code, message):
        """Helper method to close WebSocket connection with specific code and message"""
        await send({
            "type": "websocket.close",
            "code": code,
            "text": message,
        })
        
    async def __call__(self, scope, receive, send):
        try:
            # Initialize url_route if not present
            if 'url_route' not in scope:
                scope['url_route'] = {'kwargs': {}}

            # Get token from query params
            query_string = scope.get('query_string', b'').decode()
            query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
            token = query_params.get('token')

            if not token:
                logger.error('No token provided in WebSocket connection')
                return await self.close_connection(send, 4001, "No token provided")

            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                
                # Get or create user
                user = await self.get_or_create_user(user_id, token)
                
                if not user:
                    logger.error(f'User not found or could not be created for ID: {user_id}')
                    return await self.close_connection(send, 4004, "User not found")

                # Update scope with authenticated user info
                scope['user'] = user
                scope['user_id'] = user_id
                scope['url_route']['kwargs']['user_id'] = user_id
                scope['auth'] = {
                    'user': user,
                    'user_id': user_id,
                    'token': token
                }
                
                logger.debug(f"Successfully authenticated user {user_id}")
                return await super().__call__(scope, receive, send)

            except (TokenError, InvalidToken) as e:
                logger.error(f'Token validation error: {str(e)}')
                return await self.close_connection(send, 4002, "Invalid token")

        except Exception as e:
            logger.error(f'WebSocket middleware error: {str(e)}')
            return await self.close_connection(send, 4000, str(e))