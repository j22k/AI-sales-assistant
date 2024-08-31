from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import assemblyai as aai
from model import chat
chat_instance = chat()

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'flac'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_audio_to_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(audio_file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    # Save the uploaded file
    filename = secure_filename(audio_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(file_path)

    # Initialize AssemblyAI
    aai.settings.api_key = "2814292a03d94f9d9446c7f78b95e840"
    transcriber = aai.Transcriber()

    # Transcribe the audio file
    try:
        transcript = transcriber.transcribe(file_path)
        text = transcript.text
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    print(f"\n\n {text} \n\n")

    response = chat_instance.chat_to_model(text)
    print(f"\n\n{response}\n\n")
    return jsonify({'text': response})

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
