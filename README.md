# Transcendence

## Project Overview
Transcendence is a comprehensive web application that implements a real-time multiplayer Pong game with extensive features for user interaction, gameplay, and security. Our implementation exceeded the project requirements, completing 11 major modules out of the 7 required, achieving 125% completion.

## Technical Architecture

**Core Technologies**:

- Microservices Architecture: Built with 5 independent backend services
- Frontend: Vue.js 3 with Vite for fast development and optimal production builds
- Backend: Django REST Framework with Django Channels for WebSocket support
- Security: HashiCorp Vault for secrets management and ModSecurity WAF for API protection
- Database: PostgreSQL with independent databases per service
- Monitoring: ELK Stack (Elasticsearch, Logstash, Kibana) and Prometheus/Grafana
- Containerization: Docker with comprehensive Docker Compose configuration

## Modules Implemented

### Authentication System

- OAuth integration with 42 Intranet
- Two-factor authentication
- JWT token management

### User Management

- Profile customization
- Friend request system
- User search and blocking capabilities

### Pong Game

- Real-time multiplayer gameplay
- Canvas-based rendering
- Multiple device support (keyboard, touch)

### Tournament System

- Bracket visualization
- Real-time updates
- Player enrollment

### Chat System

- Private messaging
- Real-time updates via WebSockets
- Message history

### API Gateway

- NGINX with ModSecurity WAF
- SSL/TLS termination
- Request routing and load balancing

### Secret Management

- HashiCorp Vault integration
- AppRole authentication for services
- Policy-based authorization

### Monitoring and Logging

- ELK Stack for centralized logging
- Prometheus/Grafana for metrics collection
- Custom dashboards and alerts

### Database Architecture

- Service-specific PostgreSQL databases
- Data isolation and security
- Vault-managed credentials

### Internationalization

- Support for multiple languages (English, French, German)
- Dynamic language switching

### Notification System (Extra Feature)

- Real-time notifications for game invites, friend requests, etc.
- WebSocket-based delivery
- Read/unread status tracking

### Cross-Platform Compatibility

- **Device Compatibility**: Responsive design for desktop, tablet, and mobile
- **Browser Support**: Chrome, Firefox, Safari, Edge
- **Input Methods**: Keyboard, touch, and mouse controls for gameplay

## Learning Experience

### Technical Skills Acquired

- **Microservices Development**: Building and orchestrating independent services
- **Container Orchestration**: Docker Compose for complex multi-container applications
- **Security Implementation**: WAF configuration, secrets management, token-based authentication
- **Real-time Communications**: WebSockets for game, chat, and notifications
- **Full-Stack Development**: Vue.js 3 frontend with Django backend
- **Monitoring and Observability**: ELK and Prometheus/Grafana configuration

### Leadership and Soft Skills

As the team lead, this project provided invaluable experience in:

- **Project Management**: Coordinating tasks across multiple team members
- **Technical Leadership**: Making architectural decisions and guiding implementation
- **Time Management**: Meeting tight deadlines without compromising quality
- **Communication**: Ensuring clear understanding of requirements and expectations
- **Problem-Solving**: Addressing technical challenges under time constraints
- **Team Collaboration**: Creating an environment where everyone could contribute effectively

Despite facing a shortened deadline due to school curriculum updates, our team demonstrated exceptional resilience and commitment. We completed the project in just one month, maintaining high code quality and implementing all required features plus additional ones. This experience proved our ability to work efficiently under pressure while adhering to our self-imposed standards of excellence.

## Installation and Setup

### Prerequisites

- Docker and Docker Compose
- Git
- 4GB+ RAM for running all services
- 10GB+ free disk space

### Installation Steps
**Clone the repository**:

```bash
git clone https://github.com/Vikingu-del/Transcendence.git
cd Transcendence
```

**Create environment files**:
```bash
cp .env.example .env
# Edit .env file to add your specific configuration
```

**Start the application**:
```bash
docker-compose up --build -d
```

**Access the application**:
First add these lines to your `/etc/hosts` file:
```bash
127.0.0.1 localhost kibana grafana
``` 
**Then access them like this**
```bash
Frontend: https://localhost
Kibana logs: https://kibana
Grafana monitoring: https://grafana
```

**Important Configuration Options**
OAuth credentials must be configured in .env file
For development, self-signed certificates are used
For production, replace certificates with valid ones

```bash
docker-compose down
```
### Service Documentation
For more detailed information about specific components, please refer to these documents:

- [API Gateway Documentation](ApiGateway/GATEWAY.md)
- [Backend Services Overview](Backend/BACKEND.md)
- [Frontend Architecture](FrontEnd/FRONTEND.md)
- [Database Design](Database/DATABASE.md)
- [Security Implementation](Security/SECURITY.MD)
- [ELK Stack Configuration](elk/ELK.md)
- [Monitoring Setup](monitoring/MONITORING.md)


### Contributors
This project was created by:


- [Erik Seferi](https://github.com/Vikingu-del) - Team Lead
- [Ivan Petrunin](https://github.com/vanichx) - User Service 
- [Walid Mougharbel](https://github.com/wmougharbel) - Authentication Service
- [Lovejoy Andrade](https://github.com/ljoyed) - Game Service
- [Arpit Mehrotra](https://github.com/Arpit-42WOB) - DevOps

License
This project is licensed under the MIT License - see the LICENSE file for details.




