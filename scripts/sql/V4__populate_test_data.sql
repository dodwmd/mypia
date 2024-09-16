-- Insert test users
INSERT INTO users (username, email, password_hash, is_admin) VALUES
('admin', 'admin@example.com', 'hashed_password', TRUE),
('user1', 'user1@example.com', 'hashed_password', FALSE),
('user2', 'user2@example.com', 'hashed_password', FALSE);

-- Insert test tasks
INSERT INTO tasks (user_id, title, description, due_date) VALUES
(1, 'Admin Task', 'This is a task for the admin', CURRENT_TIMESTAMP + INTERVAL '1 day'),
(2, 'User1 Task', 'This is a task for user1', CURRENT_TIMESTAMP + INTERVAL '2 days'),
(3, 'User2 Task', 'This is a task for user2', CURRENT_TIMESTAMP + INTERVAL '3 days');

-- Insert test emails
INSERT INTO emails (user_id, subject, body, sender, recipient, sent_at) VALUES
(1, 'Test Email 1', 'This is a test email body', 'sender@example.com', 'admin@example.com', CURRENT_TIMESTAMP),
(2, 'Test Email 2', 'This is another test email body', 'sender@example.com', 'user1@example.com', CURRENT_TIMESTAMP);
