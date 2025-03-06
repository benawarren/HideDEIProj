from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS  # Allows cross-origin requests
import google.generativeai as genai
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enables frontend to talk to backend

#dealing with uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
stopwords = {"words": [], "phrases": []}  # Store stopwords dynamically


#create stopwords and phrases from .txt file
def load_stopwords(file_path):
    words, phrases = [], []
    with open(file_path, "r") as file:
        for line in file:
            clean_line = line.strip()
            if " " in clean_line:
                phrases.append(clean_line)
            else:
                words.append(clean_line)
    return words, phrases

# def create_stopwords():
#     print("running create_stopwords")
#     #stopwords – currently uses a list from WaPo article on NSF article reviews
#     file = open("DEIstopwords.txt", "r")
#     dei_stopwords = file.readlines()

#     print(dei_stopwords)

#     #split into phrases and words
#     phrases = []
#     words = []

#     for line in dei_stopwords:
#         if " " in line:
#             phrases.append(line.split("\n")[0])
#         else:
#             words.append(line.split("\n")[0])

#     # print(words)
#     # print(phrases)
#     return words, phrases

def process_text(title, abstract):
    #make words and phrases to replace into strings
    words_string = ", ".join(stopwords["words"])
    phrases_string = ", ".join(stopwords["phrases"])
    all_string = words_string + ", " + phrases_string

    # set api key
    api_key = "AIzaSyCUEe9Ukh87DRG_IHdBQ-Yz_GIlbvGsNkY"
    genai.configure(api_key=api_key)

    # create a model object
    model = genai.GenerativeModel("gemini-1.5-flash")

    #submit prompt
    prompt = "Rewrite the title" + title + "and the abstract" + abstract + "of an academic paper \
            so that they retain the same tone and meaning without using the words " + all_string + \
            "Take care not to use any variations of these words (i.e., their plural forms, lower-case,\
            or any term with these words as a base)"
    response = model.generate_content(prompt)

    #return response
    return response.text

@app.route('/')
def index():
    return render_template('index.html')  # Serve index.html from the templates folder

@app.route('/upload', methods=['POST'])
def upload_stopwords():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    global stopwords
    stopwords["words"], stopwords["phrases"] = load_stopwords(file_path)
    return jsonify({"message": "Stopwords uploaded successfully"})

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    title = data.get("title", "")
    abstract = data.get("abstract", "")
    result = process_text(title, abstract)
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True)
