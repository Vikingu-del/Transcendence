from channels.middleware import BaseMiddleware
from django.utils.module_loading import import_string
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip auth for sync-token endpoint
        if request.path == '/api/user/sync-token/':
            logger.debug("Skipping auth for sync-token endpoint")
            return self.get_response(request)

        if not request.path.startswith('/api/user/'):
            return self.get_response(request)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.error('No Bearer token found in request')
            return JsonResponse({'error': 'No token provided'}, status=401)

        try:
            token = auth_header.split(' ')[1]
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            # Add both user_id and user to request
            request.user_id = user_id
            try:
                request.user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.error(f'User {user_id} not found')
                return JsonResponse({'error': 'User not found'}, status=401)
                
            return self.get_response(request)
            
        except (InvalidToken, TokenError) as e:
            logger.error(f'Invalid token: {str(e)}')
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except Exception as e:
            logger.error(f'Authentication error: {str(e)}')
            return JsonResponse({'error': 'Authentication failed'}, status=401)

class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)
        self.inner = inner

    async def __call__(self, scope, receive, send):
        try:
            # Get token from query string
            query_string = scope.get('query_string', b'').decode()
            query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
            token = query_params.get('token')

            if not token:
                logger.error('No token provided in WebSocket connection')
                return await self.close_connection(send)

            try:
                # Verify JWT token
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                
                # Add user_id and connection info to scope
                scope['user_id'] = user_id
                scope['url_route'] = {"kwargs": {"user_id": user_id}}
                scope['user'] = await self.get_user(user_id)
                
                if not scope['user']:
                    logger.error(f'User {user_id} not found')
                    return await self.close_connection(send)
                
                logger.debug(f'WebSocket authenticated for user {user_id}')
                return await super().__call__(scope, receive, send)
                
            except (TokenError, InvalidToken) as e:
                logger.error(f'Token validation error: {str(e)}')
                return await self.close_connection(send)

        except Exception as e:
            logger.error(f'WebSocket middleware error: {str(e)}')
            return await self.close_connection(send)

    async def get_user(self, user_id):
        try:
            from channels.db import database_sync_to_async
            return await database_sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            return None

    async def close_connection(self, send):
        await send({
            'type': 'websocket.close',
            'code': 4003  # Custom close code for authentication failure
        })

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)