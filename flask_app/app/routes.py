# API routes for products
from flask import Blueprint, request, jsonify
from app.models import Product

# Create blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        products = Product.get_all()
        products_list = [Product.to_dict(product) for product in products]
        
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

@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID"""
    try:
        product = Product.get_by_id(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': Product.to_dict(product)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/products', methods=['POST'])
def create_product():
    """Create new product"""
    try:
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
        
        # Optional fields
        description = data.get('description', '')
        stock = data.get('stock', 0)
        category = data.get('category', 'general')
        
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
        
        # Create product
        product_id = Product.create(
            name=data['name'],
            price=price,
            description=description,
            stock=stock,
            category=category
        )
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'data': {
                'id': product_id,
                'name': data['name'],
                'price': price,
                'description': description,
                'stock': stock,
                'category': category
            }
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update existing product"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate price if provided
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    return jsonify({
                        'success': False,
                        'error': 'Price must be non-negative'
                    }), 400
                data['price'] = price
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid price format'
                }), 400
        
        # Validate stock if provided
        if 'stock' in data:
            try:
                stock = int(data['stock'])
                if stock < 0:
                    return jsonify({
                        'success': False,
                        'error': 'Stock must be non-negative'
                    }), 400
                data['stock'] = stock
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid stock format'
                }), 400
        
        # Update product
        success = Product.update(product_id, **data)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Get updated product
        updated_product = Product.get_by_id(product_id)
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully',
            'data': Product.to_dict(updated_product)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product (soft delete)"""
    try:
        success = Product.delete(product_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'success': True,
        'data': {
            'name': 'ECommerce API',
            'version': '2.0.0',
            'description': 'RESTful API for ecommerce application'
        },
        'endpoints': [
            {'method': 'GET', 'path': '/api/products', 'description': 'Get all products'},
            {'method': 'GET', 'path': '/api/products/<id>', 'description': 'Get product by ID'},
            {'method': 'POST', 'path': '/api/products', 'description': 'Create new product'},
            {'method': 'PUT', 'path': '/api/products/<id>', 'description': 'Update product by ID'},
            {'method': 'DELETE', 'path': '/api/products/<id>', 'description': 'Delete product by ID'},
            {'method': 'GET', 'path': '/api/info', 'description': 'API information'}
        ]
    })
