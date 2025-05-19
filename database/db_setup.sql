-- Create database
CREATE DATABASE IF NOT EXISTS autoclean_db;
USE autoclean_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- File uploads table
CREATE TABLE IF NOT EXISTS file_uploads (
    upload_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_size INT NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Cleaning operations table
CREATE TABLE IF NOT EXISTS cleaning_operations (
    operation_id INT AUTO_INCREMENT PRIMARY KEY,
    upload_id INT,
    operation_type VARCHAR(50) NOT NULL,
    operation_details TEXT,
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upload_id) REFERENCES file_uploads(upload_id) ON DELETE CASCADE
);

-- Cleaned files table
CREATE TABLE IF NOT EXISTS cleaned_files (
    file_id INT AUTO_INCREMENT PRIMARY KEY,
    upload_id INT,
    clean_file_path VARCHAR(255) NOT NULL,
    clean_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upload_id) REFERENCES file_uploads(upload_id) ON DELETE CASCADE
);