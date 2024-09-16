CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    key VARCHAR(50) NOT NULL,
    value VARCHAR(255),
    UNIQUE (user_id, key)
);
