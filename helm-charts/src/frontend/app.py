from flask import Flask, render_template, request, send_from_directory, jsonify
import requests
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:5000')
logger.info(f"Backend URL: {BACKEND_URL}")

@app.route('/')
def home():
    try:
        # Get websites from backend
        logger.info(f"Making GET request to {BACKEND_URL}/api/websites")
        response = requests.get(f'{BACKEND_URL}/api/websites')
        logger.info(f"Response status: {response.status_code}")
        if response.ok:
            websites = response.json()
            return render_template('home.html', websites=websites)
        else:
            return render_template('home.html', websites=[], error="Failed to fetch websites")
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return render_template('home.html', websites=[], error=str(e))

@app.route('/api/websites', methods=['GET'])
def get_websites():
    try:
        # Get websites from backend
        logger.info(f"Making GET request to {BACKEND_URL}/api/websites")
        response = requests.get(f'{BACKEND_URL}/api/websites')
        logger.info(f"Response status: {response.status_code}")
        if response.ok:
            websites = response.json()
            logger.info(f"Retrieved {len(websites) if isinstance(websites, list) else 'non-list'} websites")
            # Ensure we always return a list
            if not isinstance(websites, list):
                websites = []
            return jsonify(websites)
        else:
            logger.error(f"Backend request failed with status {response.status_code}")
            return jsonify([])
    except Exception as e:
        logger.error(f"Error in get_websites: {str(e)}")
        return jsonify([])

@app.route('/api/websites', methods=['POST'])
def add_website():
    try:
        # Forward the form data and files to backend
        logger.info("Received POST request to add website")
        logger.info(f"Form data: {request.form}")
        logger.info(f"Files: {request.files}")
        
        files = {'image': (request.files['image'].filename, request.files['image'].stream, request.files['image'].content_type)}
        data = {
            'name': request.form['name'],
            'url': request.form['url'],
            'explanation': request.form['explanation']
        }
        
        logger.info(f"Making POST request to {BACKEND_URL}/api/websites")
        response = requests.post(f'{BACKEND_URL}/api/websites', files=files, data=data)
        logger.info(f"Response status: {response.status_code}")
        
        return response.json(), response.status_code
    except Exception as e:
        logger.error(f"Error in add_website: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/websites/<website_id>', methods=['DELETE'])
def delete_website(website_id):
    try:
        logger.info(f"Making DELETE request to {BACKEND_URL}/api/websites/{website_id}")
        response = requests.delete(f'{BACKEND_URL}/api/websites/{website_id}')
        logger.info(f"Response status: {response.status_code}")
        return response.json(), response.status_code
    except Exception as e:
        logger.error(f"Error in delete_website: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/website/<website_id>')
def website_details(website_id):
    return render_template('details.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
