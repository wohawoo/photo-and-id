import cv2
from deepface import DeepFace
import json
import os

PHOTO_PATH = r'C:\Users\mylap\Desktop\project\download.jpeg'
LICENSE_PATH = r'C:\Users\mylap\Desktop\project\generated_license_0.png'

def verify_faces(photo_path, license_path):
    print("Inside verify_faces function...")
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
        print(f"Checking if photo exists at: {photo_path}")
        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"Person photo not found at: {photo_path}")
        print(f"Checking if license exists at: {license_path}")
        if not os.path.exists(license_path):
            raise FileNotFoundError(f"License image not found at: {license_path}")

        print("Attempting face verification with DeepFace...")
        verification = DeepFace.verify(
            img1_path=photo_path,
            img2_path=license_path,
            model_name=result["model"],
            detector_backend=result["detector_backend"],
            enforce_detection=True
        )
        print("DeepFace verification completed successfully.")

        result.update(verification)
        if 'distance' in result:
            result['similarity_score'] = 1 - result['distance'] if result['similarity_metric'] == 'cosine' else result['distance']

    except FileNotFoundError as fnf_error:
        result["error"] = str(fnf_error)
        print(f"FileNotFoundError caught: {result['error']}")
    except ValueError as ve:
        result["error"] = f"Face detection/verification error: {str(ve)}. Ensure clear faces are visible in both images."
        print(f"ValueError caught: {result['error']}")
    except Exception as e:
        result["error"] = f"An unexpected face verification error occurred: {str(e)}"
        print(f"Unexpected error caught: {result['error']}")

    return result

if __name__ == "__main__":
    print("Starting face verification script...")

    print(f"\n--- Step 1: Verifying Faces ({PHOTO_PATH} vs {LICENSE_PATH}) ---")
    face_verification_results = verify_faces(PHOTO_PATH, LICENSE_PATH)

    print("\nFace Verification Results Dictionary:")
    print(face_verification_results)

    if face_verification_results["error"]:
        print(f"Face Verification Error: {face_verification_results['error']}")
    else:
        print("Face Verification Results:")
        print(f"  Faces Match: {face_verification_results.get('verified', 'N/A')}")
        print(f"  Distance: {face_verification_results.get('distance', 'N/A'):.4f}")
        print(f"  Similarity Score ({face_verification_results.get('similarity_metric','N/A')} based): {face_verification_results.get('similarity_score', 'N/A'):.4f}")
        print(f"  Threshold: {face_verification_results.get('threshold', 'N/A'):.4f}")
        print(f"  Model Used: {face_verification_results.get('model', 'N/A')}")
        print(f"  Detector Backend: {face_verification_results.get('detector_backend', 'N/A')}")

    print("\nScript finished.")
