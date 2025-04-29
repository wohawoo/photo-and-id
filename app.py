from flask import Flask, request, jsonify
 from flask_cors import CORS
 import cv2
 import os
 import logging
 from werkzeug.utils import secure_filename
 import tempfile
 import gc
 import numpy as np
 import face_recognition
 
 # Configure logging
 logging.basicConfig(level=logging.DEBUG)
 logger = logging.getLogger(__name__)
 
 app = Flask(__name__)
 
 # Configure CORS
 CORS(app, resources={
     r"/api/*": {
         "origins": "*",
         "methods": ["POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"]
     }
 })
 
 app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
 
 # Set up upload directory with proper error handling
 try:
     if os.path.exists('/dev/shm'):
         upload_dir = '/dev/shm/face_verification'
         # Ensure directory exists with proper permissions
         os.makedirs(upload_dir, mode=0o755, exist_ok=True)
         logger.info(f"Using RAM-based upload directory: {upload_dir}")
     else:
         upload_dir = os.path.join(tempfile.gettempdir(), 'face_verification')
         os.makedirs(upload_dir, mode=0o755, exist_ok=True)
         logger.info(f"Using temporary directory for uploads: {upload_dir}")
     
     app.config['UPLOAD_FOLDER'] = upload_dir
 except Exception as e:
     logger.error(f"Failed to create upload directory: {str(e)}")
     # Fallback to system temp directory
     app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
     logger.info(f"Using fallback directory: {app.config['UPLOAD_FOLDER']}")
 
 ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
 MAX_IMAGE_SIZE = 400  # Maximum image dimension
 
 def allowed_file(filename):
     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
 def cleanup_files(*files):
     for file in files:
         try:
             if file and os.path.exists(file):
                 os.remove(file)
                 logger.debug(f"Cleaned up file: {file}")
         except Exception as e:
             logger.error(f"Error cleaning up file {file}: {str(e)}")
 
 def optimize_image(image_path):
     """Optimize image size to reduce memory usage"""
     try:
         img = cv2.imread(image_path)
         if img is None:
             return False
         
         # Convert to grayscale
         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
         
         # Save with high compression
         cv2.imwrite(image_path, gray, [cv2.IMWRITE_JPEG_QUALITY, 85])
         
         del img, gray
         gc.collect()
         return True
     except Exception as e:
         logger.error(f"Error optimizing image {image_path}: {str(e)}")
         return False
 
 def verify_faces(photo_path, license_path):
     logger.info("Starting face verification process")
     result = {
         "verified": False,
         "distance": None,
         "threshold": 0.6800,  # Similar to VGG-Face threshold
         "model": "VGG-Face",  # For compatibility with previous format
         "detector_backend": "opencv",
         "similarity_metric": "cosine",
         "error": None
     }
     
     try:
         if not os.path.exists(photo_path):
             raise FileNotFoundError(f"Person photo not found at: {photo_path}")
         if not os.path.exists(license_path):
             raise FileNotFoundError(f"License image not found at: {license_path}")
 
         # Optimize images
         if not optimize_image(photo_path) or not optimize_image(license_path):
             raise ValueError("Failed to process images")
 
         # Load images
         photo_image = face_recognition.load_image_file(photo_path)
         license_image = face_recognition.load_image_file(license_path)
 
         # Find faces in images
         photo_face_locations = face_recognition.face_locations(photo_image)
         license_face_locations = face_recognition.face_locations(license_image)
 
         if not photo_face_locations or not license_face_locations:
             raise ValueError("No faces detected in one or both images")
 
         # Get face encodings
         photo_encoding = face_recognition.face_encodings(photo_image, [photo_face_locations[0]])[0]
         license_encoding = face_recognition.face_encodings(license_image, [license_face_locations[0]])[0]
 
         # Calculate cosine distance
         face_distance = float(face_recognition.face_distance([photo_encoding], license_encoding)[0])
         
         # Update result with verification data - ensure all values are native Python types
         result.update({
             "verified": bool(face_distance <= result["threshold"]),
             "distance": face_distance,
             "similarity_score": float(1 - face_distance)
         })
 
         logger.info(f"""Face Verification Results:
             Faces Match: {result['verified']}
             Distance: {result['distance']:.4f}
             Similarity Score ({result['similarity_metric']} based): {result['similarity_score']:.4f}
             Threshold: {result['threshold']:.4f}
             Model Used: {result['model']}
             Detector Backend: {result['detector_backend']}""")
 
         # Clean up
         del photo_image, license_image, photo_encoding, license_encoding
         gc.collect()
 
     except FileNotFoundError as fnf_error:
         result["error"] = str(fnf_error)
         logger.error(f"File not found: {str(fnf_error)}")
     except ValueError as ve:
         result["error"] = f"Face detection error: {str(ve)}"
         logger.error(f"Value error: {str(ve)}")
     except Exception as e:
         result["error"] = f"An unexpected error occurred: {str(e)}"
         logger.error(f"Unexpected error: {str(e)}")
     finally:
         gc.collect()
     
     return result
 
 @app.route('/')
 def home():
     return jsonify({"message": "Face Verification API is running"}), 200
 
 @app.route('/api/verify', methods=['POST', 'OPTIONS'])
 def verify():
     logger.info(f"Received {request.method} request to /api/verify")
     
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
         
         # Format the response - ensure all values are native Python types
         response = {
             "status": "success",
             "result": {
                 "verified": bool(result["verified"]),
                 "distance": float(result["distance"]) if result["distance"] is not None else None,
                 "similarity_score": float(result["similarity_score"]) if result["similarity_score"] is not None else None,
                 "threshold": float(result["threshold"]),
                 "model": str(result["model"]),
                 "detector_backend": str(result["detector_backend"]),
                 "similarity_metric": str(result["similarity_metric"])
             }
         }
         
         if result.get("error"):
             response["status"] = "error"
             response["error"] = str(result["error"])
         
         return jsonify(response)
     
     except Exception as e:
         logger.error(f"Error processing request: {str(e)}")
         return jsonify({
             "status": "error",
             "error": str(e)
         }), 500
     
     finally:
         # Clean up temporary files and force garbage collection
         cleanup_files(photo_path, license_path)
         gc.collect()
 
 if __name__ == '__main__':
     port = int(os.environ.get('PORT', 8080))
     app.run(host='0.0.0.0', port=port) 
