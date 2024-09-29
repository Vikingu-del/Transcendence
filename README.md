# Transcendence
A web application that blends real-time multiplayer gaming with social interaction, allowing users to play Pong and engage in community features like chat and friend systems.

------------------------------------------------------------------------------------

EXPLANATION OF THE SUBJECT

he document describes the subject of the "ft_transcendence" project, which involves building a multiplayer online Pong game with a range of mandatory and optional modules. Key points include:

Objective: Build a website for playing the Pong game, including a real-time multiplayer feature.

Mandatory Requirements:

Minimal Technical Requirements:

Frontend with vanilla JavaScript (modifiable through the frontend module).
Backend (optional) with pure Ruby, or other frameworks if chosen.
Single-page application compatible with Chrome.
Security measures such as hashed passwords and protection against SQL injections.
Must launch using Docker.
Gameplay:

The core is an online multiplayer Pong game.
Tournament system with matchmaking.
Player registration and alias system.
Modules:

You must choose at least 7 major modules to achieve 100% completion.
Examples include User Management, AI Opponent, Live Chat, Blockchain Integration for scores, and Microservices-based backend architecture.
Security & Infrastructure: There is a heavy emphasis on security (e.g., HTTPS, JWT for authentication, and GDPR compliance).

Bonus: Additional points for completing extra minor or major modules, only if the mandatory part is perfect.

Full preview of the content can be accessed here (This should be a link to the pdf subject) .

------------------------------------------------------------------------------------

EXPLANATION OF THE MODULES WE CHOSE


Chosen Modules Overview:
7 Minor Modules:

Bootstrap (Frontend): This will provide a clean, responsive UI for your Pong game and website, simplifying layout and design tasks.
Database (PostgreSQL): Essential for storing user data, game results, and the live chat history.
Dashboard: Offers a way for users to track stats such as gameplay and win/loss records.
Game Customization: Adds flexibility to the game, allowing users to tailor the Pong or other games.
Accessibility - Support All Devices: Ensures the game is usable across phones, tablets, and desktops.
Accessibility - Expanding Browser Compatibility: Makes the web app work in multiple browsers (like Firefox and Safari).
Accessibility - Multiple Language Support: Adds multi-language functionality, crucial for broadening your audience.
6 Major Modules:

Django (Backend): A powerful backend that will manage user authentication, game logic, and database interactions. It integrates well with PostgreSQL.
Cybersecurity (2FA, JWT, Anonymization, GDPR): Protects user data and ensures compliance with GDPR regulations. This goes hand-in-hand with user management and backend security.
User Management (Standard and Remote Authentication): Provides user registration, authentication, and profiles, integrating well with Django and the security features.
Live Chat: Enhances user engagement and integrates with the user management system, allowing users to chat and invite others to games.
Another Game: Adds variety to your platform, creating a new game with matchmaking, user stats, and history.
Game Customization (from gaming): Allows flexibility for users to modify their gaming experience (power-ups, maps, etc.).
Compatibility and Integration:
Frontend (Bootstrap) works well with all other modules since it improves responsiveness and user experience across different devices.

Django Backend + PostgreSQL: Django has excellent support for PostgreSQL, so this will handle your user management, security, chat, and game logic seamlessly.

Cybersecurity Module (2FA, JWT, GDPR, etc.): This module will integrate with the user management system and the live chat to ensure all user interactions and data exchanges are secure. The use of JWT tokens will provide secure authentication across your services.

User Management (Standard + Remote Authentication): These are core modules to handle player registrations, profiles, and OAuth authentication. These modules fit well with the Django backend, and security modules like 2FA and GDPR compliance will enhance this system.

Live Chat: Adding this module integrates smoothly with user management, allowing players to communicate and invite each other to matches. The chat history can be stored in the PostgreSQL database.

Game Modules:

Game Customization will give users options to modify their gameplay experience.
Another Game adds depth to your gaming platform, which will rely on the same user management, matchmaking, and customization features already in place.
Accessibility Modules: These ensure that your app works well on different devices and browsers, and the multi-language support broadens the audience. These modules improve usability but do not interfere with the core logic, security, or user management.

Total Modules:
7 Minor Modules (Bootstrap, PostgreSQL, Dashboard, Game Customization, and 3 Accessibility modules).
6 Major Modules (Django Backend, Cybersecurity, 2 User Management, Live Chat, and Another Game).

----------------------------------------------------------------------------------------

EXPLANATION OF STEPS OF TO DO LIST:

Step 1: 
Establish the Core Backend Infrastructure (Django + PostgreSQL)
Reason: The backend forms the foundation for user management, authentication, game logic, and communication (live chat). Django is a well-suited framework for handling complex tasks like database interactions, routing, and security.
Actions:
Set up Django and PostgreSQL: Establish the database models (e.g., users, game data, chat logs).
Configure the core features like user authentication, registration, and JWT handling (for user sessions).
Create basic API endpoints for core functionalities (e.g., logging in, starting a game).
By getting this solid backend foundation, you ensure that all future modules—user management, chat, game functionality—will have a reliable and scalable base to build on.

Step 2: 
Implement Basic Frontend (Bootstrap + Django Integration)
Reason: With your backend ready, a clean UI is the next logical step. Bootstrap helps quickly scaffold a responsive and modern-looking user interface for user registration, game interactions, and more.
Actions:
Set up Django templates or API to deliver frontend content.
Use Bootstrap to create responsive forms and views (e.g., login, game, chat).

Step 3: 
Implement User Management and Security Modules (2FA, JWT, GDPR)
Reason: User management and security are critical for ensuring the integrity of your platform. It will tie into all other modules that involve user interactions, like the live chat, games, and dashboards.
Actions:
Implement user registration, login, and profile management.
Add JWT-based authentication to secure API requests.
Implement 2FA for added security.
Ensure GDPR compliance (e.g., user data anonymization and deletion features).

Step 4: 
Add Gameplay Features and Real-Time Interaction (Live Chat + Games)
Reason: Now that you have a strong backend, secure user management, and a responsive UI, you can focus on the main interactive features of the project.
Actions:
Build real-time gameplay (Pong) using Django with WebSockets (channels).
Implement live chat so players can communicate, invite others to play, etc.
Work on tournaments and matchmaking systems.

Step 5: 
Expand with Additional Games, Customizations, and Dashboards
Reason: By now, the main structure is in place, and you can start to enhance the platform with extra features that build on the foundation.
Actions:
Add the Game Customization and Another Game module to offer variety to users.
Implement Dashboards for stats, user histories, and live game data.

Step 6: 
Add Accessibility Features (Device Support, Browser Compatibility, Language Support)
Reason: These features are important but do not affect core functionality. They improve user experience and help make the platform more inclusive.
Actions:
Ensure the site works across all devices and browsers.
Add multi-language support to broaden the user base.

----------------------------------------------------------------------------------------

CHAT GPT SUGESTION WHERE TO START

Recommended Starting Point:
Focus on Step 1: Backend (Django + PostgreSQL) first.

This step will set up the base of your entire system, allowing smooth expansion into more complex features (security, user management, games) without requiring major changes later.
Expanding Afterward:
Once the backend is solid, add the frontend and user management/security, and then proceed with gameplay and interactivity (chat, games). This staged approach avoids reworking code and allows testing each feature thoroughly before expanding.

----------------------------------------------------------------------------------------

step-by-step guide to set up a Django-PostgreSQL backend for your project:

Step 1: Set Up the Development Environment
Install Django and psycopg2 (PostgreSQL adapter):

Ensure you have pip installed and run the following:
bash
Copy code
pip install django psycopg2
Install PostgreSQL:

On Linux:
bash
Copy code
sudo apt update
sudo apt install postgresql postgresql-contrib
On Mac (via Homebrew):
bash
Copy code
brew install postgresql
Start PostgreSQL:

On Linux:
bash
Copy code
sudo service postgresql start
On Mac:
bash
Copy code
brew services start postgresql
Step 2: Create a PostgreSQL Database
Log into the PostgreSQL command line:

bash
Copy code
sudo -u postgres psql
Create a new user and database:

sql
Copy code
CREATE DATABASE pong_db;
CREATE USER pong_user WITH PASSWORD 'your_password';
ALTER ROLE pong_user SET client_encoding TO 'utf8';
ALTER ROLE pong_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pong_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pong_db TO pong_user;
Exit the PostgreSQL prompt:

sql
Copy code
\q
Step 3: Create a New Django Project
Start a new Django project:

bash
Copy code
django-admin startproject pong_project
cd pong_project
Configure PostgreSQL in settings.py: Open the settings.py file in your project and update the DATABASES setting:

python
Copy code
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pong_db',
        'USER': 'pong_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
Step 4: Apply Migrations and Test the Connection
Make migrations:

bash
Copy code
python manage.py makemigrations
python manage.py migrate
Create a superuser (admin account):

bash
Copy code
python manage.py createsuperuser
Run the server to test if everything is working:

bash
Copy code
python manage.py runserver
Open http://127.0.0.1:8000/ in your browser to see if Django is running successfully.

Step 5: Organize Your Project Structure
Create the core apps:

For users and authentication:
bash
Copy code
python manage.py startapp users
For the game logic:
bash
Copy code
python manage.py startapp game
Register these apps in pong_project/settings.py by adding them to the INSTALLED_APPS list:

python
Copy code
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'game',
]
Step 6: Create Models for Users and Game Data
In users/models.py, define a basic User model (extend AbstractUser if needed):

python
Copy code
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Add any additional user-related fields here
    pass
In game/models.py, define models for your game:

python
Copy code
from django.db import models
from users.models import CustomUser

class PongGame(models.Model):
    player1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='player1_games')
    player2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='player2_games')
    score_player1 = models.IntegerField(default=0)
    score_player2 = models.IntegerField(default=0)
    game_date = models.DateTimeField(auto_now_add=True)
Make and apply migrations:

bash
Copy code
python manage.py makemigrations users game
python manage.py migrate
Step 7: Set Up Django Admin for Models
In users/admin.py:

python
Copy code
from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

admin.site.register(CustomUser, UserAdmin)
In game/admin.py:

python
Copy code
from django.contrib import admin
from .models import PongGame

admin.site.register(PongGame)
Visit the admin panel by running the server and navigating to /admin.

Summary of Steps:
Install Django, PostgreSQL, and set up a new Django project.
Configure PostgreSQL and set up the database connection.
Create essential apps (users, game), and define the models for users and game logic.
Set up the Django admin to manage users and games.
With this backend ready, you can now easily integrate additional modules like JWT authentication, 2FA, and game logic.

----------------------------------------------------------------------------------------

Using Vue.js for your frontend, given the modules you've chosen, is a great idea. Vue is highly compatible with modern development practices and will work well with the modules you plan to implement. Here's why and how it fits in with your project:

Why Vue.js Is a Good Fit for Your Project:
Component-Based Architecture:

Vue’s component-based design allows for modular development. You can build isolated, reusable components (like game boards, user profiles, chat windows, etc.) which aligns well with the modular structure of your project.
Single-Page Application (SPA):

Your project requires a single-page application (SPA), where the user can interact with multiple views (e.g., game, user profile, chat) without reloading the page. Vue.js is specifically designed for this purpose.
Vue Router enables you to handle multiple views seamlessly while maintaining a single-page feel.
Integration with Bootstrap:

Vue easily integrates with Bootstrap for responsive, clean UI components. You can either:
Use BootstrapVue to wrap Bootstrap components as Vue components.
Directly integrate Bootstrap via CSS/JavaScript for simpler needs.
Interactivity and Real-Time Features:

For real-time interaction (like the live Pong game and chat), Vue works smoothly with WebSockets or libraries like Vuex for state management, making it easier to handle multiplayer games, live chat, and matchmaking.
User Management & Authentication:

Vue's lightweight nature allows easy integration with backend services like Django for user authentication and JWT handling, which you've included in your modules.
How Vue Fits with Your Chosen Modules:
Frontend Modules:
Bootstrap minor module: Vue integrates well with Bootstrap, providing a strong foundation for a responsive UI.
Game Customization (minor): Vue's dynamic nature allows for easy real-time UI updates, where users can customize game settings (e.g., power-ups, maps).
Another Game (major): Vue makes it easier to create a scalable front end with reusable components, which will be necessary as you add multiple games to the platform.
User Management, Security, and Chat:
Live Chat (major): Vue works seamlessly with WebSocket libraries or Axios for real-time chat communication.
User Management (major): Vue’s ease of state management (with Vuex) will help maintain user profiles, game histories, and stats across different views.
JWT, 2FA, GDPR Compliance (major): Vue can interact with your Django backend for secure authentication, data handling, and implementing GDPR-compliant features like user data deletion.
Accessibility and Responsive Design:
Support on all devices: Vue works well with responsive libraries (like Bootstrap), and it can adapt well to mobile, tablet, and desktop.
Expanding Browser Compatibility: Vue apps are lightweight and can be made cross-browser compatible easily.
Multiple Language Support: Vue has strong internationalization (i18n) support, making it easy to manage multi-language features.
Conclusion:
Vue is a good choice for your project given the flexibility, modularity, and performance it offers. It integrates seamlessly with the frontend and backend technologies you're using (Bootstrap, Django, PostgreSQL), and it’s particularly strong for building interactive, real-time applications like the one you're planning.

Recommended Next Steps:
Set up Vue for your project.
Integrate BootstrapVue or direct Bootstrap for the frontend UI.
Build out the core components for user management, games, and chat using Vue's component-based system.