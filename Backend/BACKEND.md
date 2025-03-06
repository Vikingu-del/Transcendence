# Backend Architecture Overview

## Service Architecture
The backend of your Transcendence application uses a microservices architecture with the following key components:
### Authentication Service (Port 8001)
Authentication Service (Port 8001)
Purpose: Centralized authentication and authorization
Key Features:
JWT token generation and validation
OAuth integration with 42 Intranet
Two-factor authentication (QR code generation)
User registration and login
Tech Stack:
Django REST Framework
SimpleJWT for token handling
PostgreSQL database (auth_db)
Gunicorn WSGI server
### User Service (Port 8000)
User Service (Port 8000)
Purpose: User profile and relationship management
Key Features:
Profile creation and management
Friend request system (add/accept/decline)
User search functionality
Block user capability
Online status tracking
Tech Stack:
Django REST Framework
Django Channels for WebSockets
PostgreSQL database (user_db)
Media file handling for avatars
### Chat Service (Port 8002)
Chat Service (Port 8002)
Purpose: Real-time messaging between users
Key Features:
Private chat conversations
Real-time message delivery
Message history storage and retrieval
Consistent chat ID generation (user1_id_user2_id)
Tech Stack:
Django REST Framework
Django Channels for WebSockets
Redis for WebSocket backing
PostgreSQL database (chat_db)
### Game Service (Port 8005)
Game Service (Port 8005)
Purpose: Pong game and tournament management
Key Features:
Real-time gameplay using WebSockets
Match history tracking
Game session management
Tournament functionality
Tech Stack:
Django REST Framework
Django Channels for WebSockets
Redis for WebSocket backing
PostgreSQL database (game_db)
### Notification Service (Port 8006)
Notification Service (Port 8006)
Purpose: System-wide notification handling
Key Features:
Push notifications for various events
Read/unread status tracking
Real-time notification delivery
Notification history
Tech Stack:
Django REST Framework
Django Channels for WebSockets
Redis for WebSocket backing
PostgreSQL database (notification_db)
## API Gateway
API Gateway
Purpose: Entry point for all client requests
Key Features:
Request routing to appropriate services
SSL/TLS termination
Web Application Firewall via ModSecurity
Load balancing
CORS handling
Tech Stack:
NGINX
ModSecurity for security
Custom SSL certificate handling
## Inter-Service Communication
Inter-Service Communication
The services communicate with each other through:

HTTP REST APIs:

Each service exposes endpoints for other services to consume
Services make HTTP requests to each other for data or actions
Example: Chat service fetches user data from User service
JWT Authentication:

All services use the same JWT secret key (your-secret-key-here)
Services verify tokens with the Auth service via /api/user/verify/ endpoint
JWT middleware in each service handles token validation
Common Authentication Middleware:

Each service implements similar JWT middleware classes:
JWTAuthMiddleware for HTTP requests
TokenAuthMiddleware for WebSocket connections
These middlewares verify tokens and create/fetch user objects
User Synchronization:

Services maintain synchronized user data through the User service
When a new user is encountered, services create a local copy of user data

user, created = User.objects.get_or_create(
    id=user_id,
    defaults={
        'username': user_data.get('username'),
        'email': user_data.get('email')
    }
)

WebSockets for Real-time Communication:

Chat, Game, and Notification services use WebSockets
Redis is used as the channel layer backend
## Security Mechanisms
Security Mechanisms
JWT Token-based Authentication:

Access tokens (60 min) and refresh tokens (1 day)
Token verification across services
ModSecurity WAF in API Gateway:

Protection against OWASP Top 10 vulnerabilities
Request/response inspection
Custom security rules
Environment-based Configuration:

Sensitive configuration retrieved from environment variables
Vault integration for secrets management
Cross-Origin Resource Sharing (CORS):

Configured in each service and the API Gateway
## Database Structure
Database Structure
Each service has its own dedicated PostgreSQL database
Services maintain minimal copies of user data from the User service
## Deployment
Deployment
All services are containerized using Docker
Each service has its own Dockerfile with specific configurations
Services use entrypoint scripts that handle:
Database connection checking
Migration application
Secret retrieval from Vault
Service startup
This architecture provides a scalable, maintainable approach with clear separation of concerns between different functional areas of the application.