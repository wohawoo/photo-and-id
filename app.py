from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
from deepface import DeepFace
import os
import logging
from werkzeug.utils import secure_filename
import tempfile
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS to allow requests from any origin
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_files(*files):
    for file in files:
        try:
            if file and os.path.exists(file):
                os.remove(file)
        except Exception as e:
            logger.error(f"Error cleaning up file {file}: {str(e)}")

def verify_faces(photo_path, license_path):
    logger.info("Starting face verification process")
    result = {
        "verified": None,
        "distance": None,
        "threshold": None,
        "model": "VGG-Face",
        "detector_backend": "opencv",
        "similarity_metric": "cosine",
        "error": None
    }
    
    try:
        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"Person photo not found at: {photo_path}")
        if not os.path.exists(license_path):
            raise FileNotFoundError(f"License image not found at: {license_path}")

        logger.info("Running DeepFace verification")
        verification = DeepFace.verify(
            img1_path=photo_path,
            img2_path=license_path,
            model_name=result["model"],
            detector_backend=result["detector_backend"],
            enforce_detection=True
        )

        result.update(verification)
        if 'distance' in result:
            result['similarity_score'] = 1 - result['distance'] if result['similarity_metric'] == 'cosine' else result['distance']
        
        logger.info("Face verification completed successfully")

    except FileNotFoundError as fnf_error:
        logger.error(f"File not found error: {str(fnf_error)}")
        result["error"] = str(fnf_error)
    except ValueError as ve:
        logger.error(f"Face detection error: {str(ve)}")
        result["error"] = f"Face detection/verification error: {str(ve)}. Ensure clear faces are visible in both images."
    except Exception as e:
        logger.error(f"Unexpected error in face verification: {str(e)}")
        result["error"] = f"An unexpected face verification error occurred: {str(e)}"
    finally:
        # Force garbage collection
        gc.collect()
    
    return result

@app.route('/')
def home():
    return jsonify({"message": "Face Verification API is running"}), 200

@app.route('/api/verify', methods=['POST', 'OPTIONS'])
def verify():
    logger.info(f"Received {request.method} request to /api/verify")
    
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response

    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405
        
    if 'photo' not in request.files or 'license' not in request.files:
        return jsonify({'error': 'Both photo and license files are required'}), 400
    
    photo = request.files['photo']
    license = request.files['license']
    
    if photo.filename == '' or license.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not (allowed_file(photo.filename) and allowed_file(license.filename)):
        return jsonify({'error': 'Invalid file type. Allowed types: png, jpg, jpeg'}), 400
    
    photo_path = None
    license_path = None
    
    try:
        # Save files temporarily
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(photo.filename))
        license_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(license.filename))
        
        logger.info(f"Saving uploaded files to {photo_path} and {license_path}")
        photo.save(photo_path)
        license.save(license_path)
        
        # Verify faces
        result = verify_faces(photo_path, license_path)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up temporary files
        cleanup_files(photo_path, license_path)
        gc.collect()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 