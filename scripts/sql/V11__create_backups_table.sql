CREATE TABLE backups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    backup_path VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20)
);
