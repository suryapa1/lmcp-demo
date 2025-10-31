-- SQLite Sample Database Schema
-- This creates a simple database with sample data for testing

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    category TEXT,
    in_stock BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    total_price REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Insert sample users
INSERT INTO users (name, email, role) VALUES
    ('Alice Johnson', 'alice@example.com', 'admin'),
    ('Bob Smith', 'bob@example.com', 'user'),
    ('Carol White', 'carol@example.com', 'user'),
    ('David Brown', 'david@example.com', 'user');

-- Insert sample products
INSERT INTO products (name, description, price, category, in_stock) VALUES
    ('Laptop', 'High-performance laptop for development', 1299.99, 'Electronics', 1),
    ('Wireless Mouse', 'Ergonomic wireless mouse', 29.99, 'Accessories', 1),
    ('Mechanical Keyboard', 'RGB mechanical keyboard', 159.99, 'Accessories', 1),
    ('Monitor', '27-inch 4K monitor', 449.99, 'Electronics', 1),
    ('USB-C Hub', '7-in-1 USB-C hub', 49.99, 'Accessories', 1),
    ('Webcam', 'HD webcam with microphone', 79.99, 'Electronics', 0),
    ('Desk Lamp', 'LED desk lamp', 39.99, 'Office', 1),
    ('Office Chair', 'Ergonomic office chair', 299.99, 'Furniture', 1);

-- Insert sample orders
INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES
    (1, 1, 1, 1299.99, 'completed'),
    (1, 3, 1, 159.99, 'completed'),
    (2, 2, 2, 59.98, 'completed'),
    (2, 5, 1, 49.99, 'shipped'),
    (3, 4, 1, 449.99, 'pending'),
    (4, 7, 1, 39.99, 'completed');

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
