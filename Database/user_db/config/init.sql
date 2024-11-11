-- Drop existing users table if it exists
DROP TABLE IF EXISTS users CASCADE;

-- Create simplified users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,                   -- Unique ID for each user
    username VARCHAR(100) UNIQUE NOT NULL,   -- Unique username
    email VARCHAR(100) UNIQUE NOT NULL,      -- Unique email
    password VARCHAR(255) NOT NULL,          -- Hashed password
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date user joined
);
