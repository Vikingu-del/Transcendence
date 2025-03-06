# Frontend Architecture Overview

## Core Technologies
- **Vue.js 3**: Component-based frontend framework
- **Vite**: Fast, modern build tool and development server
- **Vue Router**: Client-side routing for single-page application
- **Vuex**: State management pattern and library
- **WebSockets**: Real-time bidirectional communication
- **i18n**: Internationalization support for multiple languages

## Component Architecture

### Authentication Components
- **Login**: OAuth integration with 42 Intranet
- **Register**: New user registration
- **Token Management**:
### Game Components
- **GameView**: Core Pong game implementation
  - Canvas-based rendering
  - Real-time game state management
  - Keyboard and touch input handling
- **GlobalGame**: Reusable game component for different contexts
  - Game invitations system
  - Tournament integration
  - Score tracking

### Tournament Components
- **Tournament**: Tournament bracket visualization
  - Semi-finals and finals display
  - Real-time tournament status updates
  - Player enrollment system
### Social Components
- **Friends**: Friend management system
  - Friend requests (send/accept/decline)
  - Online status tracking
  - User search functionality
  - Block user capability
- **Chat**: Real-time messaging
  - Private conversations
  - Message history
  - Real-time message delivery
  - WebSocket-based communication

### Profile Components
- **Profile**: User profile management
  - Avatar upload
  - Display name customization
  - Settings configuration
### Notification System
- **Notifications**: Real-time notification delivery
  - Game invitations
  - Friend requests
  - Tournament updates
  - Cross-component notification handling

## State Management

### Vuex Store Structure
- **Authentication**: Token storage and validation
- **User**: User profile and preferences
- **Game**: Game state and invitations
- **Notifications**: Unread notification count

### Key Store Functionality
- Token refresh mechanism
## Internationalization

### Supported Languages:
- English
- French
- German

### Translation Implementation:
- Vue i18n plugin
- JSON-based translation files
- Dynamic language switching
- Persistent language preferences

## Communication Layer

### Backend API Integration
RESTful API consumption for:
### WebSocket Connections
- **Chat WebSockets**: Real-time message delivery
- **Game WebSockets**:
  - Real-time game state synchronization
  - Player movements
  - Score updates
  - Game events
- **Tournament WebSockets**: Real-time tournament progression
- **Notification WebSockets**: Push notifications

### Connection Management
- Automatic reconnection
- Token authentication for WebSockets
- Error handling and recovery
## UI/UX Design

### Design System
- Consistent color scheme
- Responsive layout
- Dark/Light mode support
- Animation transitions

### Key UI Components
- Modal dialogs
- Notification banners
- Game interface elements
## Security Features

### Frontend Security
- XSS protection
- CSRF prevention
- Secure token handling
- Input validation

### Authentication Flow
- Token validation on protected routes
- Automatic token refresh when expired
```markdown
## Development and Deployment

### Development Setup
- Vite development server
- Hot module replacement
- ESLint configuration for code quality
- Environment-specific configurations

### Build Process
- Production optimization
- Asset minification
- Code splitting
- Source map generation

### Deployment Configuration
- Docker containerization
- Nginx static file serving
- Environment variable integration
- API proxy configuration
