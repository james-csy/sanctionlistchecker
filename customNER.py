import spacy
import json

from spacy.tokens import DocBin


def customModel():
    nlp = spacy.load("en_core_web_sm")
    with open("NER_data.json", "r") as read_file:
        data = json.load(read_file)
        training_data = data["annotations"]

    # the DocBin will store the example documents
    db = DocBin()
    for text, annotations in training_data:
        doc = nlp(text)
        ents = []
        for start, end, label in annotations["entities"]:
            span = doc.char_span(start, end, label=label)
            ents.append(span)
        doc.ents = ents
        db.add(doc)
    db.to_disk("./train.spacy")
