CREATE TABLE email_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    subject VARCHAR(255),
    sender VARCHAR(120),
    recipient VARCHAR(120),
    timestamp TIMESTAMP WITH TIME ZONE,
    is_sent BOOLEAN
);
