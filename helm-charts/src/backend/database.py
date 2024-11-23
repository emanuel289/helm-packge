import os
from pymongo import MongoClient
from bson import ObjectId
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Get MongoDB connection details from environment variables or use defaults
        mongodb_host = os.getenv('MONGODB_HOST', 'mongodb')
        mongodb_port = int(os.getenv('MONGODB_PORT', '27017'))
        mongodb_user = os.getenv('MONGODB_USER', 'root')
        mongodb_password = os.getenv('MONGODB_PASSWORD', 'secretpassword')
        mongodb_database = os.getenv('MONGODB_DATABASE', 'websitedb')

        # Construct the MongoDB connection URI with connection options
        mongodb_uri = f"mongodb://{mongodb_user}:{mongodb_password}@{mongodb_host}:{mongodb_port}/{mongodb_database}?authSource=admin&retryWrites=true&w=majority"
        
        max_retries = 5
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                # Connect to MongoDB with server selection timeout
                self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
                # Test the connection
                self.client.admin.command('ping')
                self.db = self.client[mongodb_database]
                self.collection = self.db.websites
                logger.info("Successfully connected to MongoDB")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to connect to MongoDB (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to connect to MongoDB after {max_retries} attempts: {str(e)}")
                    raise

    def add_website(self, website_data):
        try:
            result = self.collection.insert_one(website_data)
            logger.info(f"Successfully added website with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error adding website to database: {str(e)}")
            raise

    def get_all_websites(self):
        try:
            websites = list(self.collection.find())
            # Convert ObjectId to string for JSON serialization
            for website in websites:
                website['_id'] = str(website['_id'])
            logger.info(f"Retrieved {len(websites)} websites from database")
            return websites
        except Exception as e:
            logger.error(f"Error retrieving websites from database: {str(e)}")
            raise

    def delete_website(self, website_id):
        try:
            result = self.collection.delete_one({'_id': ObjectId(website_id)})
            if result.deleted_count == 0:
                logger.warning(f"No website found with ID: {website_id}")
                raise ValueError("Website not found")
            logger.info(f"Successfully deleted website with ID: {website_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting website from database: {str(e)}")
            raise
