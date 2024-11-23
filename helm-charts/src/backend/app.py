from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import Database
import base64
import logging
import os
from PIL import Image
import io

app = Flask(__name__)
# Enable CORS for all origins
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()

def is_valid_image(file):
    # Check if file exists
    if not file:
        return False, "No file provided"
    
    # Check file type
    allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
    if file.content_type not in allowed_types:
        return False, f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
    
    # Check file size (5MB limit) using chunks to avoid memory issues
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 5 * 1024 * 1024:  # 5MB in bytes
        return False, "File size too large. Maximum size is 5MB"
    
    try:
        # Verify it's a valid image by attempting to open it
        image = Image.open(file)
        image.verify()
        file.seek(0)
        return True, None
    except Exception as e:
        file.seek(0)
        return False, "Invalid image file"

def optimize_image(image_file, max_size=(800, 800)):
    try:
        # Read image data
        image = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        elif image.mode not in ['RGB', 'L']:
            image = image.convert('RGB')
        
        # Calculate new dimensions while maintaining aspect ratio
        width, height = image.size
        if width > max_size[0] or height > max_size[1]:
            ratio = min(max_size[0] / width, max_size[1] / height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save optimized image to bytes
        output = io.BytesIO()
        image.save(output, format='JPEG', optimize=True, quality=85)
        return output.getvalue()
    except Exception as e:
        logger.error(f"Error optimizing image: {str(e)}")
        raise

@app.route('/api/')
def index():
    return jsonify({
        "status": "online",
        "message": "Star Trek Website Collection API",
        "endpoints": {
            "GET /api/websites": "Get all websites",
            "POST /api/websites": "Add a new website",
            "DELETE /api/websites/<id>": "Delete a website",
            "GET /api/health": "Health check"
        }
    })

@app.route('/api/websites', methods=['GET'])
def get_websites():
    try:
        websites = db.get_all_websites()
        logger.info(f"Retrieved {len(websites)} websites")
        return jsonify(websites)
    except Exception as e:
        logger.error(f"Error retrieving websites: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/websites', methods=['POST'])
def add_website():
    try:
        # Log received data
        logger.info("Received website addition request")
        logger.info(f"Form data: {request.form}")
        logger.info(f"Files: {request.files}")

        # Validate required fields
        if 'name' not in request.form:
            return jsonify({"error": "Name is required"}), 400
        if 'url' not in request.form:
            return jsonify({"error": "URL is required"}), 400
        if 'explanation' not in request.form:
            return jsonify({"error": "Explanation is required"}), 400
        if 'image' not in request.files:
            return jsonify({"error": "Image is required"}), 400

        image_file = request.files['image']
        if not image_file.filename:
            return jsonify({"error": "No image file selected"}), 400
        
        # Validate image
        is_valid, error_message = is_valid_image(image_file)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        try:
            # Optimize image
            optimized_image = optimize_image(image_file)
            image_data = base64.b64encode(optimized_image).decode('utf-8')
            logger.info(f"Image processed and optimized. Size: {len(image_data)} bytes")
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return jsonify({"error": "Failed to process image"}), 400

        # Create website data
        website_data = {
            'name': request.form['name'].strip(),
            'url': request.form['url'].strip(),
            'explanation': request.form['explanation'].strip(),
            'image': {
                'data': image_data,
                'contentType': 'image/jpeg'  # We convert all images to JPEG
            }
        }

        # Add to database
        result = db.add_website(website_data)
        logger.info(f"Website added successfully: {result}")
        
        return jsonify({"message": "Website added successfully", "id": str(result)}), 201

    except Exception as e:
        logger.error(f"Error adding website: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/websites/<website_id>', methods=['DELETE'])
def delete_website(website_id):
    try:
        db.delete_website(website_id)
        logger.info(f"Website deleted successfully: {website_id}")
        return jsonify({"message": "Website deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting website: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'version': '1.0.0'
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
