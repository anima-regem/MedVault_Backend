import os
from PIL import Image
import requests as rq
from io import BytesIO
import google.generativeai as genai
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
# import speech_recognition as sr


load_dotenv()

# class PrescriptionRequest(BaseModel):
#     prescription_image: str
app = Flask(__name__)
# app = FastAPI()
# GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print(GOOGLE_API_KEY)

# Define a route
@app.post("/get-prescription")
def get_prescription():
    model1 = genai.GenerativeModel('gemini-pro-vision')
    request_body = request.json.get("prescription_image")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = rq.get(request_body, headers=headers)
    genai.configure(api_key=GOOGLE_API_KEY)
    image = None
    if response.status_code == 200:
        image_content = BytesIO(response.content)
        try:
            # Try to open the image
            image = Image.open(image_content)

        except Exception as image_open_error:
            # Log the error and handle it appropriately
            logging.error(f"Error opening image: {str(image_open_error)}")
    else:
        return "Image not found"

    # Check if image is not None before passing it to the model
    if image:
        google_response = model1.generate_content(["from the image return a json file of lost of pills along with how many times it should be taken and any other remark as an object; name:str, dose:str, frequency:number, remarks:long natural language str; return json data only without language marking", image], stream=False)
        google_response.resolve()
        # json_response = json.loads(google_response.text)
        gl_final = google_response.text.replace("```json", "").replace("```", "")
        print(gl_final)
        return jsonify(gl_final)

model2 = genai.GenerativeModel('gemini-pro')
@app.post("/chat")
def chat():
    print(request.json)
    chat_message = request.json.get("message")
    print(chat_message)
    response = model2.generate_content("You are Bloom, a medical assistance chatbot that can give answer to any medical relaed question and not any other type of question;\n"+chat_message, stream=False)
    return response.text

# def convert_audio_to_text():
#     # Check if the POST request contains a file with key 'audio'
#     if 'audio' not in request.files:
#         return jsonify({'error': 'No audio file provided'}), 400

#     audio_file = request.files['audio']

#     # Check if the file has a valid extension (e.g., WAV or MP3)
#     if audio_file and audio_file.filename.lower().endswith(('.wav', '.mp3')):
#         recognizer = sr.Recognizer()

#         # Read the audio file using SpeechRecognition
#         with sr.AudioFile(audio_file) as source:
#             audio_data = recognizer.record(source)

#         # Perform speech-to-text conversion
#         text_result = recognizer.recognize_google(audio_data)

#         return jsonify({'result': text_result})

#     else:
#         return jsonify({'error': 'Invalid audio file format'}), 400


if __name__ == '__main__':
    app.run(debug=True)