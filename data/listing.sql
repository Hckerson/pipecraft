
CREATE TABLE listing (
    id TEXT PRIMARY KEY UNIQUE,
    name VARCHAR(255) NOT NULL,
    email TEXT NOT NULL,
    source_id INT,
    amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

