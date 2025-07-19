CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    skills TEXT,
    workload INT
);

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    required_skills TEXT,
    priority VARCHAR(50),
    assigned_to INT,
    assigned_by_ai TINYINT(1),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
