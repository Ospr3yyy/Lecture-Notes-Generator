# Lecture-Notes-Generator
NLP-Based Lecture Notes Generator Web App for Students Using Speech-to-Text and Text Summarizer Models


# Setup
**REQUIRES PYTHON 3.90**

- pip install flask
- pip install flask-pymongo
- pip install transformers
- pip install 'transformers[torch]'
- pip install mysql-connector-python

# Current functionalities
- 5 webpages:
  - login
    - email check (currently only neoaurellano@gmail.com)
    - password check (currently only 12345)
  - index
    - home page
    - upload audio file
    - view uploaded files
    - view results  
  - uploads
    - view uploaded files
    - embedded audio file (not yet working)
  - results
    - view results (transcribed and summarized)
    - download file not yet working
  - test
    - for checking connection to localhost only
    - is not redirected from anywhere else

- can upload audio files
  - file type accepted: mp3 only tested so far
  
- both transformer models working
  - speech to text
  - text summarizer

- model tests: general, neutral English
- model performace: 7.5/10, satisfactory

# CHECKLIST
- implement front-end framework to reduce ugliness
- improve front-end elements
- connect to database
- create account system
  - sign up
  - log in
- store files and results to database
