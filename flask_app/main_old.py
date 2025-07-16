from flask import Flask, render_template, request, jsonify
import os
import sqlite3
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['DEBUG'] = True
app.config['DATABASE'] = 'ecommerce.db'

# Database helper functions
def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db_connection()
    
    # Create products table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            description TEXT,
            stock INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data if table is empty
    if conn.execute('SELECT COUNT(*) FROM products').fetchone()[0] == 0:
        sample_products = [
            ('Laptop', 999.99, 'High-performance laptop', 10),
            ('Mouse', 29.99, 'Wireless mouse', 50),
            ('Keyboard', 79.99, 'Mechanical keyboard', 25)
        ]
        
        conn.executemany('''
            INSERT INTO products (name, price, description, stock) 
            VALUES (?, ?, ?, ?)
        ''', sample_products)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Sample data (we'll replace this with database later)
app_info = {
    'name': 'ECommerce API',
    'version': '1.0.0',
    'startup_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

# Basic route - Home page
@app.route('/')
def home():
    return render_template('home.html')

# Health check endpoint - More detailed for backend monitoring
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'ECommerce API is running',
        'app_info': app_info,
        'timestamp': datetime.now().isoformat()
    })

# API endpoint to get app information
@app.route('/api/info')
def api_info():
    return jsonify({
        'success': True,
        'data': app_info,
        'endpoints': [
            {'method': 'GET', 'path': '/', 'description': 'Home page'},
            {'method': 'GET', 'path': '/health', 'description': 'Health check'},
            {'method': 'GET', 'path': '/api/info', 'description': 'API information'},
            {'method': 'GET', 'path': '/api/products', 'description': 'Get all products'},
            {'method': 'GET', 'path': '/api/products/<id>', 'description': 'Get product by ID'},
            {'method': 'POST', 'path': '/api/products', 'description': 'Create new product'},
            {'method': 'PUT', 'path': '/api/products/<id>', 'description': 'Update product by ID'},
            {'method': 'DELETE', 'path': '/api/products/<id>', 'description': 'Delete product by ID'}
        ]
    })

# Database API endpoints
@app.route('/api/products')
def get_products():
    """Get all products from database"""
    try:
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM products ORDER BY id').fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        products_list = []
        for product in products:
            products_list.append({
                'id': product['id'],
                'name': product['name'],
                'price': float(product['price']),
                'description': product['description'],
                'stock': product['stock'],
                'created_at': product['created_at']
            })
        
        return jsonify({
            'success': True,
            'data': products_list,
            'count': len(products_list)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    """Get single product by ID"""
    try:
        conn = get_db_connection()
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        conn.close()
        
        if product is None:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': product['id'],
                'name': product['name'],
                'price': float(product['price']),
                'description': product['description'],
                'stock': product['stock'],
                'created_at': product['created_at']
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        required_fields = ['name', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate data types
        try:
            price = float(data['price'])
            if price < 0:
                return jsonify({
                    'success': False,
                    'error': 'Price must be non-negative'
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid price format'
            }), 400
        
        # Optional fields with defaults
        description = data.get('description', '')
        stock = data.get('stock', 0)
        
        # Validate stock
        try:
            stock = int(stock)
            if stock < 0:
                return jsonify({
                    'success': False,
                    'error': 'Stock must be non-negative'
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid stock format'
            }), 400
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO products (name, price, description, stock) 
            VALUES (?, ?, ?, ?)
        ''', (data['name'], price, description, stock))
        
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'data': {
                'id': product_id,
                'name': data['name'],
                'price': price,
                'description': description,
                'stock': stock
            }
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Check if product exists
        conn = get_db_connection()
        existing_product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        
        if existing_product is None:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []
        
        if 'name' in data:
            update_fields.append('name = ?')
            update_values.append(data['name'])
        
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    conn.close()
                    return jsonify({
                        'success': False,
                        'error': 'Price must be non-negative'
                    }), 400
                update_fields.append('price = ?')
                update_values.append(price)
            except ValueError:
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'Invalid price format'
                }), 400
        
        if 'description' in data:
            update_fields.append('description = ?')
            update_values.append(data['description'])
        
        if 'stock' in data:
            try:
                stock = int(data['stock'])
                if stock < 0:
                    conn.close()
                    return jsonify({
                        'success': False,
                        'error': 'Stock must be non-negative'
                    }), 400
                update_fields.append('stock = ?')
                update_values.append(stock)
            except ValueError:
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'Invalid stock format'
                }), 400
        
        if not update_fields:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'No valid fields to update'
            }), 400
        
        # Execute update
        update_values.append(product_id)
        query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, update_values)
        conn.commit()
        
        # Get updated product
        updated_product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully',
            'data': {
                'id': updated_product['id'],
                'name': updated_product['name'],
                'price': float(updated_product['price']),
                'description': updated_product['description'],
                'stock': updated_product['stock'],
                'created_at': updated_product['created_at']
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        conn = get_db_connection()
        
        # Check if product exists
        existing_product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        
        if existing_product is None:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Delete the product
        conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)