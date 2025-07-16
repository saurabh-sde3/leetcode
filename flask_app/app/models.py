# Database models and operations
import sqlite3
from datetime import datetime
from flask import current_app

class DatabaseManager:
    """Database operations manager"""
    
    @staticmethod
    def get_connection():
        """Get database connection"""
        if current_app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:'):
            db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
        else:
            # For future AWS RDS integration
            raise NotImplementedError("PostgreSQL/MySQL connections not implemented yet")
    
    @staticmethod
    def init_database():
        """Initialize database with tables"""
        conn = DatabaseManager.get_connection()
        
        # Create products table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                description TEXT,
                stock INTEGER DEFAULT 0,
                category TEXT DEFAULT 'general',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create categories table for future use
        conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert sample data if tables are empty
        if conn.execute('SELECT COUNT(*) FROM products').fetchone()[0] == 0:
            sample_products = [
                ('Laptop', 999.99, 'High-performance laptop', 10, 'electronics'),
                ('Mouse', 29.99, 'Wireless mouse', 50, 'electronics'),
                ('Keyboard', 79.99, 'Mechanical keyboard', 25, 'electronics'),
                ('Coffee Mug', 15.99, 'Ceramic coffee mug', 100, 'home'),
                ('Notebook', 8.99, 'Spiral notebook', 200, 'office')
            ]
            
            conn.executemany('''
                INSERT INTO products (name, price, description, stock, category) 
                VALUES (?, ?, ?, ?, ?)
            ''', sample_products)
        
        # Insert sample categories
        if conn.execute('SELECT COUNT(*) FROM categories').fetchone()[0] == 0:
            sample_categories = [
                ('electronics', 'Electronic devices and accessories'),
                ('home', 'Home and kitchen items'),
                ('office', 'Office supplies and equipment'),
                ('clothing', 'Apparel and accessories'),
                ('books', 'Books and educational materials')
            ]
            
            conn.executemany('''
                INSERT INTO categories (name, description) 
                VALUES (?, ?)
            ''', sample_categories)
        
        conn.commit()
        conn.close()

class Product:
    """Product model with CRUD operations"""
    
    @staticmethod
    def get_all():
        """Get all products"""
        conn = DatabaseManager.get_connection()
        products = conn.execute('''
            SELECT * FROM products WHERE is_active = 1 ORDER BY id
        ''').fetchall()
        conn.close()
        return products
    
    @staticmethod
    def get_by_id(product_id):
        """Get product by ID"""
        conn = DatabaseManager.get_connection()
        product = conn.execute('''
            SELECT * FROM products WHERE id = ? AND is_active = 1
        ''', (product_id,)).fetchone()
        conn.close()
        return product
    
    @staticmethod
    def create(name, price, description='', stock=0, category='general'):
        """Create new product"""
        conn = DatabaseManager.get_connection()
        cursor = conn.execute('''
            INSERT INTO products (name, price, description, stock, category) 
            VALUES (?, ?, ?, ?, ?)
        ''', (name, price, description, stock, category))
        
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    @staticmethod
    def update(product_id, **kwargs):
        """Update product with provided fields"""
        conn = DatabaseManager.get_connection()
        
        # Check if product exists
        existing = conn.execute('''
            SELECT * FROM products WHERE id = ? AND is_active = 1
        ''', (product_id,)).fetchone()
        
        if not existing:
            conn.close()
            return False
        
        # Build dynamic update query
        update_fields = []
        update_values = []
        
        allowed_fields = ['name', 'price', 'description', 'stock', 'category']
        for field in allowed_fields:
            if field in kwargs:
                update_fields.append(f'{field} = ?')
                update_values.append(kwargs[field])
        
        if update_fields:
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            update_values.append(product_id)
            
            query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
            conn.execute(query, update_values)
            conn.commit()
        
        conn.close()
        return True
    
    @staticmethod
    def delete(product_id):
        """Soft delete product (set is_active = 0)"""
        conn = DatabaseManager.get_connection()
        
        # Check if product exists
        existing = conn.execute('''
            SELECT * FROM products WHERE id = ? AND is_active = 1
        ''', (product_id,)).fetchone()
        
        if not existing:
            conn.close()
            return False
        
        # Soft delete
        conn.execute('''
            UPDATE products SET is_active = 0, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (product_id,))
        
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def to_dict(product_row):
        """Convert database row to dictionary"""
        if not product_row:
            return None
        
        return {
            'id': product_row['id'],
            'name': product_row['name'],
            'price': float(product_row['price']),
            'description': product_row['description'],
            'stock': product_row['stock'],
            'category': product_row['category'],
            'is_active': bool(product_row['is_active']),
            'created_at': product_row['created_at'],
            'updated_at': product_row['updated_at']
        }
