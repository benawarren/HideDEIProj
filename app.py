from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Allows cross-origin requests
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # Enables frontend to talk to backend

#create stopwords and phrases from .txt file
def create_stopwords():
    print("running create_stopwords")
    #stopwords – currently uses a list from WaPo article on NSF article reviews
    file = open("DEIstopwords.txt", "r")
    dei_stopwords = file.readlines()

    print(dei_stopwords)

    #split into phrases and words
    phrases = []
    words = []

    for line in dei_stopwords:
        if " " in line:
            phrases.append(line.split("\n")[0])
        else:
            words.append(line.split("\n")[0])

    # print(words)
    # print(phrases)
    return words, phrases

def process_text(title, abstract):
    words, phrases = create_stopwords()

    # set api key
    api_key = "XXXXXXXXXXXXXXXXXXXXXXXXXX"
    genai.configure(api_key=api_key)

    # create a model object
    model = genai.GenerativeModel("gemini-1.5-flash")

    #make words and phrases to replace into strings
    words_string = ", ".join(words)
    phrases_string = ", ".join(phrases)
    all_string = words_string + phrases_string
    # print(all_string)

    print("submitting prompt")
    #submit prompt
    prompt = "Rewrite the title" + title + "and the abstract" + abstract + "of an academic paper \
            so that they retain the same tone and meaning without using the words " + all_string + \
            "Take care not to use any variations of these words (i.e., their plural forms, lower-case,\
            or any term with these words as a base)"
    response = model.generate_content(prompt)

    #return response
    print("Returning response")
    # print("Here is your de-DEI-ified output:")
    # print(response)
    return response.text

@app.route('/')
def index():
    return render_template('index.html')  # Serve index.html from the templates folder

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    title = data.get("title", "")
    abstract = data.get("abstract", "")
    result = process_text(title, abstract)
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True)
