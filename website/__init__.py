from flask import Flask, session, request, render_template, redirect, url_for, flash, send_from_directory
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
    app.config['TEMP_FOLDER'] = 'temp/'
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
    os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
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
                    session['uid'] = user['uid']
                    return redirect(url_for('index'))
                else:
                    flash('Invalid email or password', 'danger')
            
            except mysql.connector.Error as err:
                flash(f"Error: {err}", 'danger')
            finally:
                cur.close()
                connection.close()
            
        return render_template('login.html')

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

            # Connect to DB
            connection = mysql.connector.connect(**db_config)

            if file:
                filename = secure_filename(file.filename)
                temp = os.path.join(app.config['TEMP_FOLDER'], filename)
                
                # Create temp file for audio transcription
                file.save(temp)
                    
                # read file as binary
                file.seek(0)
                audio_file = file.read()
                
                try:
                    upload_query = """
                    INSERT INTO audio_file (title, file)
                    VALUES (%s, %s)
                    """
                    cur = connection.cursor()
                    
                    cur.execute(upload_query, (filename, audio_file))
                    
                    #audio_db_data = cur.fetchone()
                    file_id = cur.lastrowid
                    connection.commit()
                    
                    flash('Audio file uploaded successfully as a file in the database!', 'success')
                except mysql.connector.Error as err:
                    flash(f"Database error: {err}", 'danger')
                    print(err)
                finally:
                    cur.close()

                # Process audio file (speech-to-text and summarization)
                transcribed_text = transcribe_audio(temp, speech_to_text_pipeline)
                summarized_text = summarize_text(transcribed_text, summarization_pipeline)
                    
                # Save results to db
                try:
                    content = f"Transcription:\n{transcribed_text}\n\nSummary:\n{summarized_text}"
                    txt_data = content.encode('utf-8')
                    result_query = """
                        INSERT INTO note (file_id, uid, title, transcribed_file)
                        VALUES (%s, %s, %s, %s)
                    """
                    cur = connection.cursor()
                    cur.execute(result_query, (file_id, session['uid'], f'{filename}_results.txt', txt_data))
                    connection.commit()
                    flash('Notes successfully created as a file in the database!', 'success')
                except mysql.connector.Error as err:
                    flash(f"Database error: {err}", 'danger')
                finally:
                    cur.close()
                    connection.close()

                # Delete temp file
                try:
                    if os.path.exists(temp):
                        os.remove(temp)
                    else:
                        flash('Temporary file not found, could not be deleted', 'warning')
                except Exception as e:
                    flash('Audio file uploaded successfully as a file in the database!', 'success')

                return render_template('summary.html', transcription=transcribed_text, summary=summarized_text)

        return render_template('uploads.html')
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/uploads')
    def uploaded_files():
        # List all files in db
        connection = mysql.connector.connect(**db_config)
        try:
            get_audio_query = """
                SELECT audio_file.title
                FROM audio_file
                JOIN note ON audio_file.file_id = note.file_id
                WHERE note.uid = %s
            """
            cur = connection.cursor()
            
            cur.execute(get_audio_query, (session['uid'],))
            audio_files = [row[0] for row in cur.fetchall()]
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')
            print(err)
        finally:
            cur.close()
            connection.close()
        #audio_files = os.listdir(app.config['UPLOAD_FOLDER'])
        return render_template('uploads.html', audio_files=audio_files)
    
    
    @app.route('/results/<path:filename>')
    def uploaded_result(filename):
        return send_from_directory(app.config['RESULT_FOLDER'], filename)
    
    @app.route('/results')
    def uploaded_results():
        # List all files in the results directory and read their contents
        connection = mysql.connector.connect(**db_config)
        try:
            get_results_query = """
                SELECT *
                FROM note
                WHERE note.uid = %s
            """
            cur = connection.cursor()
            cur.execute(get_results_query, (session['uid'],))
            results=cur.fetchall()
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')
            print(err)
        finally:
            cur.close()
            connection.close()
        #result_files = os.listdir(app.config['RESULT_FOLDER'])
        summaries = {}
        
        '''for filename in result_files:
            with open(os.path.join(app.config['RESULT_FOLDER'], filename), 'r') as file:
                summaries[filename] = file.read()  # Read content of each result file'''
                
        for row in results:
            blob_data = row[4]
            decoded_text = blob_data.decode('utf-8')
            summaries[row[3]] = decoded_text

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