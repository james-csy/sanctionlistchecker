import spacy
import json



def customModel():
    nlp = spacy.load("en_core_web_sm")
    with open("NER_data.json", "r") as read_file:
        data = json.load(read_file)
        trainingData = data["annotations"]
