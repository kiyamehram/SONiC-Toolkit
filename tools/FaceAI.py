import face_recognition
import cv2
import os
import numpy as np
from datetime import datetime
import exifread
import requests
from io import BytesIO
from PIL import Image, ImageDraw
import sqlite3
import matplotlib.pyplot as plt

class AdvancedFaceAI:
    def __init__(self, db_path='face_database.db'):

        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS faces
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      encoding BLOB,
                      source TEXT,
                      date_added TEXT,
                      metadata TEXT)''')
        conn.commit()
        conn.close()

    def _store_face(self, name, encoding, source='', metadata=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO faces (name, encoding, source, date_added, metadata) VALUES (?, ?, ?, ?, ?)",
                  (name, encoding.tobytes(), source, datetime.now().isoformat(), str(metadata)))
        conn.commit()
        conn.close()

    def load_from_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT name, encoding FROM faces")
        rows = c.fetchall()
        conn.close()
        
        known_encodings = []
        known_names = []
        for name, encoding_blob in rows:
            known_names.append(name)
            known_encodings.append(np.frombuffer(encoding_blob, dtype=np.float64))
        
        return known_encodings, known_names

    def load_and_encode_faces(self, folder_path, store_in_db=False):
        known_encodings = []
        known_names = []
        
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(folder_path, filename)
                try:
                    metadata = self._extract_metadata(image_path)
                    
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    
                    if len(encodings) > 0:
                        name = os.path.splitext(filename)[0]
                        known_encodings.append(encodings[0])
                        known_names.append(name)
                        
                        if store_in_db:
                            self._store_face(name, encodings[0], source=image_path, metadata=metadata)
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
        
        return known_encodings, known_names

    def _extract_metadata(self, image_path):
        metadata = {}
        
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f)
                for tag in tags.keys():
                    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                        metadata[str(tag)] = str(tags[tag])
        except:
            pass
            
        return metadata

    def recognize_faces(self, image_path, known_encodings=None, known_names=None, output_image=None, tolerance=0.6):
        if known_encodings is None or known_names is None:
            known_encodings, known_names = self.load_from_db()
        
        if image_path.startswith('http'):
            response = requests.get(image_path)
            image = face_recognition.load_image_file(BytesIO(response.content))
        else:
            image = face_recognition.load_image_file(image_path)
            
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        results = []
        pil_image = Image.fromarray(image)
        draw = ImageDraw.Draw(pil_image)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance)
            name = "Unknown"
            confidence = "N/A"
            
            if True in matches:
                matched_idxs = [i for i, match in enumerate(matches) if match]
                distances = face_recognition.face_distance(known_encodings, face_encoding)
                best_match_idx = np.argmin(distances)
                name = known_names[best_match_idx]
                confidence = f"{round((1 - distances[best_match_idx]) * 100, 2)}%"
            
            results.append({
                'name': name,
                'confidence': confidence,
                'location': (top, right, bottom, left),
                'encoding': face_encoding
            })
            
            draw.rectangle(((left, top), (right, bottom)), outline=(0, 255, 0))
            text_width, text_height = draw.textsize(name)
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 255, 0), outline=(0, 255, 0))
            draw.text((left + 6, bottom - text_height - 5), f"{name} ({confidence})", fill=(0, 0, 0))
        
        if output_image:
            pil_image.save(output_image)
            print(f"Result image saved to {output_image}")
        
        return results

    def webcam_recognition(self):
        video_capture = cv2.VideoCapture(0)
        known_encodings, known_names = self.load_from_db()
        
        while True:
            ret, frame = video_capture.read()
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                name = "Unknown"
                
                if True in matches:
                    matched_idxs = [i for i, match in enumerate(matches) if match]
                    distances = face_recognition.face_distance(known_encodings, face_encoding)
                    best_match_idx = np.argmin(distances)
                    name = known_names[best_match_idx]
                
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 1)
            
            cv2.imshow('Face Recognition', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        video_capture.release()
        cv2.destroyAllWindows()

    def search_similar_faces(self, target_encoding, threshold=0.7):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, name, encoding, source FROM faces")
        rows = c.fetchall()
        conn.close()
        
        similar_faces = []
        for row in rows:
            db_id, name, encoding_blob, source = row
            db_encoding = np.frombuffer(encoding_blob, dtype=np.float64)
            distance = face_recognition.face_distance([target_encoding], db_encoding)[0]
            similarity = 1 - distance
            
            if similarity >= threshold:
                similar_faces.append({
                    'id': db_id,
                    'name': name,
                    'similarity': f"{round(similarity * 100, 2)}%",
                    'source': source
                })
        
        return sorted(similar_faces, key=lambda x: x['similarity'], reverse=True)

    def visualize_results(self, image_path, results):
        if image_path.startswith('http'):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_path)
        
        draw = ImageDraw.Draw(image)
        
        for result in results:
            top, right, bottom, left = result['location']
            name = result['name']
            confidence = result['confidence']
            
            draw.rectangle(((left, top), (right, bottom)), outline=(0, 255, 0))
            text_width, text_height = draw.textsize(f"{name} ({confidence})")
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 255, 0), outline=(0, 255, 0))
            draw.text((left + 6, bottom - text_height - 5), f"{name} ({confidence})", fill=(0, 0, 0))
        
        plt.figure(figsize=(12, 8))
        plt.imshow(image)
        plt.axis('off')
        plt.show()

if __name__ == "__main__":
    print("""
▄████  ██   ▄█▄    ▄███▄       ██   ▄█ 
█▀   ▀ █ █  █▀ ▀▄  █▀   ▀      █ █  ██ 
█▀▀    █▄▄█ █   ▀  ██▄▄        █▄▄█ ██ 
█      █  █ █▄  ▄▀ █▄   ▄▀     █  █ ▐█ 
 █        █ ▀███▀  ▀███▀          █  ▐ 
  ▀      █                       █     
        ▀                       ▀      
    """)
    
    face_ai = AdvancedFaceAI()
    
    print("[1] Loading known faces...")
    face_ai.load_and_encode_faces("known_faces", store_in_db=True)
    
    print("[2] Recognizing faces in unknown image...")
    results = face_ai.recognize_faces("unknown.jpg", output_image="output.jpg")
    print("\nDetection Results:")
    for result in results:
        print(f"- {result['name']} (Confidence: {result['confidence']})")
    
    print("\n[3] Visualizing results...")
    face_ai.visualize_results("unknown.jpg", results)
    
    print("\n[4] Searching for similar faces...")
    sample_face = face_recognition.load_image_file("sample_face.jpg")
    sample_encoding = face_recognition.face_encodings(sample_face)[0]
    similar = face_ai.search_similar_faces(sample_encoding)
    print("\nSimilar Faces Found:")
    for face in similar:
        print(f"- {face['name']} ({face['similarity']}) - Source: {face['source']}")
    
    print("\n[5] Starting webcam recognition (press 'q' to quit)...")
    face_ai.webcam_recognition()