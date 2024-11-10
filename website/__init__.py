from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
import mysql.connector
from werkzeug.utils import secure_filename
from transformers import pipeline
import os
import librosa

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['UPLOAD_FOLDER'] = 'uploads/'
    app.config['RESULT_FOLDER'] = 'results/'  # Folder to save results
    
    db_config = {
        'host': 'localhost',
        'user': 'root',  # your MySQL username
        'password': '',  # your MySQL password
        'database': '120l',  # your database name
        'ssl_disabled': True
    }

    # Initialize Transformers pipelines
    speech_to_text_pipeline = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-large-960h")
    summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")

    # Ensure upload and result directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

    # Routes
    @app.route('/')
    def start():
        return render_template('login.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        connection = mysql.connector.connect(**db_config)
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            try:
                # Use dictionary=True to fetch results as a dictionary
                cur = connection.cursor(dictionary=True)
                cur.execute('SELECT * FROM user WHERE email = %s', (email,))
                user = cur.fetchone()
                
                if user and user['password'] == password:
                    return redirect(url_for('index'))
                else:
                    flash('Invalid email or password', 'danger')
            
            except mysql.connector.Error as err:
                flash(f"Error: {err}", 'danger')
            finally:
                cur.close()
                connection.close()
            
        return render_template('login.html')  # Render the login form template

    @app.route('/index')
    def index(): 
        return render_template('index.html')

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            if 'audio_file' not in request.files:
                flash('No file part')
                return redirect(request.url)

            file = request.files['audio_file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Process audio file (speech-to-text and summarization)
                transcribed_text = transcribe_audio(filepath, speech_to_text_pipeline)
                summarized_text = summarize_text(transcribed_text, summarization_pipeline)

                # Save results to a local file
                result_filename = f"{os.path.splitext(filename)[0]}_results.txt"
                result_filepath = os.path.join(app.config['RESULT_FOLDER'], result_filename)

                with open(result_filepath, 'w') as result_file:
                    result_file.write("Transcription:\n")
                    result_file.write(transcribed_text + "\n\n")
                    result_file.write("Summary:\n")
                    result_file.write(summarized_text)

                return render_template('summary.html', transcription=transcribed_text, summary=summarized_text)

        return render_template('uploads.html')
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/uploads')
    def uploaded_files():
        # List all files in the uploads directory
        audio_files = os.listdir(app.config['UPLOAD_FOLDER'])
        return render_template('uploads.html', audio_files=audio_files)
    
    
    @app.route('/results/<path:filename>')
    def uploaded_result(filename):
        return send_from_directory(app.config['RESULT_FOLDER'], filename)
    
    @app.route('/results')
    def uploaded_results():
        # List all files in the results directory and read their contents
        result_files = os.listdir(app.config['RESULT_FOLDER'])
        summaries = {}
        
        for filename in result_files:
            with open(os.path.join(app.config['RESULT_FOLDER'], filename), 'r') as file:
                summaries[filename] = file.read()  # Read content of each result file

        return render_template('results.html', summaries=summaries)
    
    @app.route('/test')
    def test_db():
        try:
            # Establish connection using mysql-connector-python
            connection = mysql.connector.connect(**db_config)
            
            # Test the database connection by running a simple query
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            
            # Return the name of the connected database
            return f"Connected to database: {db_name[0]}"
        
        except mysql.connector.Error as e:
            # Catch MySQL errors and return the error message
            return f"Error: {str(e)}"
        
        finally:
            # Ensure the connection is closed after use
            if connection.is_connected():
                cursor.close()
                connection.close()



    return app

def transcribe_audio(filepath, pipeline):
    """Converts audio file to text using Speech-to-Text pipeline."""
    # Load the audio file
    audio_array, _ = librosa.load(filepath, sr=16000)  # Use a sample rate of 16kHz
    transcription = pipeline(audio_array)
    return transcription['text']

def summarize_text(text, pipeline):
    """Summarizes text using Summarization pipeline."""
    summary = pipeline(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)