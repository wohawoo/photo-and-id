from flask import Flask, request, render_template, jsonify
import cv2
from deepface import DeepFace
import os
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def verify_faces(photo_path, license_path):
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

    except FileNotFoundError as fnf_error:
        result["error"] = str(fnf_error)
    except ValueError as ve:
        result["error"] = f"Face detection/verification error: {str(ve)}. Ensure clear faces are visible in both images."
    except Exception as e:
        result["error"] = f"An unexpected face verification error occurred: {str(e)}"

    return result

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    if 'photo' not in request.files or 'license' not in request.files:
        return jsonify({'error': 'Both photo and license files are required'}), 400
    
    photo = request.files['photo']
    license = request.files['license']
    
    if photo.filename == '' or license.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not (allowed_file(photo.filename) and allowed_file(license.filename)):
        return jsonify({'error': 'Invalid file type. Allowed types: png, jpg, jpeg'}), 400
    
    try:
        # Save files temporarily
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(photo.filename))
        license_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(license.filename))
        
        photo.save(photo_path)
        license.save(license_path)
        
        # Verify faces
        result = verify_faces(photo_path, license_path)
        
        # Clean up temporary files
        os.remove(photo_path)
        os.remove(license_path)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 