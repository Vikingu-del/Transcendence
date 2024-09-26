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