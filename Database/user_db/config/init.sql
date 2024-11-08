-- Drop(Delete) existing tables if they exist and create new tables
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS friends CASCADE;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY, --Unique ID for each user
    username VARCHAR(100) UNIQUE NOT NULL, --Unique username
    email VARCHAR(100) UNIQUE NOT NULL, --Unique email
    password VARCHAR(255) NOT NULL, --Hashed password
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP --Date user joined
);

-- Create user_profiles table
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY, --Unique ID for each user profile
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, --User ID
    display_name VARCHAR(100) UNIQUE NOT NULL, --Unique display name
    avatar VARCHAR(255) DEFAULT 'avatars/default.png', --Avatar image URL
    wins INTEGER DEFAULT 0, --Number of wins
    losses INTEGER DEFAULT 0, --Number of losses
    match_history TEXT --Match history
);

-- Create friends table
CREATE TABLE friends (
    id SERIAL PRIMARY KEY, --Unique ID for each friend
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, --User ID
    friend_id INTEGER REFERENCES users(id) ON DELETE CASCADE, --Friend ID
    UNIQUE (user_id, friend_id) --Unique pair of user and friend
);