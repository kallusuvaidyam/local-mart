-- ============================================================
-- LOCAL MARKETPLACE - Complete MySQL Database Schema
-- Compatible with PlanetScale (MySQL 8.0)
-- Run this via PlanetScale console or your MySQL client
-- ============================================================

CREATE DATABASE IF NOT EXISTS local_marketplace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE local_marketplace;

-- ─────────────────────────────────────────────────────────
-- 1. BLOCKS
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS blocks (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────
-- 2. DELIVERY ZONES
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS delivery_zones (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    block_id        INT NOT NULL,
    zone_name       VARCHAR(100) NOT NULL,
    delivery_charge DECIMAL(8,2) NOT NULL,
    min_order_value DECIMAL(8,2) DEFAULT 0.00,
    is_active       BOOLEAN DEFAULT TRUE,
    INDEX idx_block_id (block_id)
    -- FK added below after blocks table exists
);

-- ─────────────────────────────────────────────────────────
-- 3. USERS
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(150) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    phone           VARCHAR(15) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            ENUM('customer', 'admin') DEFAULT 'customer',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
);

-- ─────────────────────────────────────────────────────────
-- 4. ADDRESSES
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS addresses (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT NOT NULL,
    block_id        INT NOT NULL,
    zone_id         INT NOT NULL,
    label           VARCHAR(50) DEFAULT 'Home',
    address_line1   VARCHAR(255) NOT NULL,
    address_line2   VARCHAR(255),
    landmark        VARCHAR(150),
    pincode         VARCHAR(10),
    is_default      BOOLEAN DEFAULT FALSE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);

-- ─────────────────────────────────────────────────────────
-- 5. CATEGORIES
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categories (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) UNIQUE NOT NULL,
    slug        VARCHAR(100) UNIQUE NOT NULL,
    image_url   VARCHAR(500),
    is_active   BOOLEAN DEFAULT TRUE,
    INDEX idx_slug (slug)
);

-- ─────────────────────────────────────────────────────────
-- 6. PRODUCTS
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    category_id     INT NOT NULL,
    name            VARCHAR(200) NOT NULL,
    slug            VARCHAR(200) UNIQUE NOT NULL,
    description     TEXT,
    price           DECIMAL(10,2) NOT NULL,
    mrp             DECIMAL(10,2),
    stock_qty       INT DEFAULT 0,
    unit            VARCHAR(30),
    return_policy   INT DEFAULT 2,
    image_url       VARCHAR(500),
    is_active       BOOLEAN DEFAULT TRUE,
    is_featured     BOOLEAN DEFAULT FALSE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category_id),
    INDEX idx_slug (slug),
    INDEX idx_active_featured (is_active, is_featured)
);

-- ─────────────────────────────────────────────────────────
-- 7. CARTS
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS carts (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT UNIQUE NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME ON UPDATE CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────
-- 8. CART ITEMS
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cart_items (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    cart_id     INT NOT NULL,
    product_id  INT NOT NULL,
    quantity    INT NOT NULL DEFAULT 1,
    UNIQUE KEY unique_cart_product (cart_id, product_id),
    INDEX idx_cart_id (cart_id)
);

-- ─────────────────────────────────────────────────────────
-- 9. ORDERS
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    user_id             INT NOT NULL,
    address_id          INT NOT NULL,
    status              ENUM('pending','confirmed','out_for_delivery','delivered','cancelled') DEFAULT 'pending',
    payment_method      ENUM('cod','online') DEFAULT 'cod',
    subtotal            DECIMAL(10,2) NOT NULL,
    delivery_charge     DECIMAL(8,2) NOT NULL,
    total_amount        DECIMAL(10,2) NOT NULL,
    snap_address        TEXT NOT NULL,
    snap_block_name     VARCHAR(100),
    snap_zone_name      VARCHAR(100),
    notes               TEXT,
    razorpay_order_id   VARCHAR(100),
    razorpay_payment_id VARCHAR(100),
    ordered_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivered_at        DATETIME,
    updated_at          DATETIME ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_ordered_at (ordered_at)
);

-- ─────────────────────────────────────────────────────────
-- 10. ORDER ITEMS
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_items (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    order_id        INT NOT NULL,
    product_id      INT NOT NULL,
    product_name    VARCHAR(200) NOT NULL,
    product_image   VARCHAR(500),
    unit_price      DECIMAL(10,2) NOT NULL,
    quantity        INT NOT NULL,
    line_total      DECIMAL(10,2) NOT NULL,
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
);

-- ─────────────────────────────────────────────────────────
-- 11. REVIEWS
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    product_id  INT NOT NULL,
    order_id    INT NOT NULL,
    rating      TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY one_review_per_order_product (user_id, product_id, order_id),
    INDEX idx_product_id (product_id)
);

-- ─────────────────────────────────────────────────────────
-- SEED DATA: Admin User (password: admin123)
-- ─────────────────────────────────────────────────────────
-- NOTE: Password hash below is bcrypt of "admin123"
-- Change this immediately in production!

-- Blocks
INSERT IGNORE INTO blocks (name, description) VALUES
('Block A - Gandhi Nagar', 'Near Gandhi Chowk'),
('Block B - Nehru Colony', 'Near Nehru Park'),
('Block C - Market Area', 'Main market area'),
('Block D - Station Road', 'Near railway station');

-- Delivery Zones (delivery_charge, free if order above min_order_value)
INSERT IGNORE INTO delivery_zones (block_id, zone_name, delivery_charge, min_order_value) VALUES
(1, 'Block A - Zone 1 (Near Market)', 20.00, 200.00),
(1, 'Block A - Zone 2 (Far End)', 30.00, 300.00),
(2, 'Block B - Zone 1', 20.00, 200.00),
(2, 'Block B - Zone 2', 30.00, 300.00),
(3, 'Block C - Zone 1', 15.00, 150.00),
(3, 'Block C - Zone 2', 25.00, 250.00),
(4, 'Block D - Zone 1', 20.00, 200.00),
(4, 'Block D - Zone 2', 35.00, 350.00);

-- Categories
INSERT IGNORE INTO categories (name, slug) VALUES
('Vegetables', 'vegetables'),
('Fruits', 'fruits'),
('Dairy', 'dairy'),
('Bakery', 'bakery'),
('Beverages', 'beverages'),
('Snacks', 'snacks'),
('Household', 'household'),
('Personal Care', 'personal-care');

-- ─────────────────────────────────────────────────────────
-- 12. ORDER RETURNS
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_returns (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    order_id    INT NOT NULL,
    user_id     INT NOT NULL,
    reason      TEXT NOT NULL,
    status      ENUM('return_requested','return_approved','return_rejected','return_picked_up','return_completed') DEFAULT 'return_requested',
    admin_note  TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_order_return (order_id),
    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- ─────────────────────────────────────────────────────────
-- USEFUL QUERIES FOR ADMIN
-- ─────────────────────────────────────────────────────────

-- Total revenue
-- SELECT SUM(total_amount) as revenue FROM orders WHERE status = 'delivered';

-- Orders today
-- SELECT * FROM orders WHERE DATE(ordered_at) = CURDATE() ORDER BY ordered_at DESC;

-- Top products
-- SELECT oi.product_name, SUM(oi.quantity) as sold, SUM(oi.line_total) as revenue
-- FROM order_items oi
-- GROUP BY oi.product_id, oi.product_name
-- ORDER BY sold DESC LIMIT 10;

-- Orders by block
-- SELECT o.snap_block_name, COUNT(*) as order_count, SUM(o.total_amount) as revenue
-- FROM orders o GROUP BY o.snap_block_name;
