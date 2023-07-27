from flask import Flask, render_template, request
from thefuzz import fuzz
import csv
from forms import SanctionSearch, SanctionSearchList, ExcelUploadWithLabels
from werkzeug.utils import secure_filename

#import for excel file handling
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np

#import openpyxl
#description import
import spacy
from spacy import displacy


app = Flask(__name__)
app.config['SECRET_KEY'] = "sanctionsearch"

#//--------------------------------------------------------------------------------------------------------------------------------------

#? Helper Functions

#define common words
with open("files/common.txt") as f:
    whitelist = [str(line)[:-1] for line in list(f)]

#extracts names from sanction lists and outputs list of names
def readSanctionList():
        with open('files/sdn.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            names = []
            for row in csv_reader:
                names.append(row["NAME"])
            #print(f'Processed {line_count} lines.')
        return names

#function to remove common words from search (e.g. "corporation" or "inc")
def removeCommon(name):
    result = ""
    common = ""
    for i in name.split(" "):
        if i not in whitelist:
            result += (i + " ")
        else:
            common += (i + " ")
    return result, common

#return names with the highest partial_ratio score
def searchSanction(nameToSearch):
    upperName = nameToSearch.upper()
    cleanUpperName, common = removeCommon(upperName)
    print(f"Name: {upperName}, Common: {common}")
    scores = {}
    high_scores = {}
    flag = False
    for name in readSanctionList():
         try:
            scores[str(name)] = fuzz.token_set_ratio(name, cleanUpperName)
            if scores[str(name)] >= 80:
                if common == "" or fuzz.token_set_ratio(name, upperName) > 50:
                    high_scores[str(name)] = scores[str(name)]
                    flag = True
         except:
            scores[str(name)] = 0
    return dict(sorted(high_scores.items(), key=lambda item: item[1], reverse=True)), flag

#returns dictionary in dictionary of all names that want to be searched and their relevant scores
def searchSanctionMany(namesToSearch):
    searchResult = {}
    for name in namesToSearch:
        sanctionResult, flag = searchSanction(name)
        searchResult[name] = {"scores": sanctionResult, "flag":flag}
        #add if highest score greater than x value, True (or flag)
    return searchResult

#helper function for readExcel() that writes results to an excel file
def writeExcel(df, path):
    with pd.ExcelWriter(path, mode = 'a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name="Sheet2")
    return "Success"

#reads "Name" column of the given excel file and performs sanctionSearch on each name. returns a view of all names and their results
def readExcel():
    df = pd.read_excel(r'files/searchNames.xlsx')
    
    #print(type(df["Name"]))
    searchResult = searchSanctionMany(df["Name"].to_numpy())
    toExcel = pd.DataFrame(searchResult).T
    writeExcel(toExcel, "files/searchNames.xlsx")
    return render_template("excelSearchResult.html", searchResult = searchResult)

#function that extracts names and locations from descriptions
def extractNamesFromDescriptions(descriptions):
    locations = []
    names = []
    nlp = spacy.load("en_core_web_sm")
    for d in descriptions:
        analyzer = nlp(d)
        for ent in analyzer.ents:
            if ent.label_ in ["Person", "ORG"]:
                names += [ent.text]
            elif ent.label_ == "GPE":
                locations += [ent.text]
    return names, locations

#take inputs of excel file and names of columns and then perform a sanction search on everything relevant
def readMultipleExcelColumns(df, name = "Name", desc = "Event Description", loca = "Loss Location"):
    namesResult = []
    descNames = []
    descLocations = []
    allLoca = []
    try:
        #set function only keeps unique values
        allNames = list(set(df[name].to_numpy()))
        print(f"{len(allNames)} Companies & Names")
    except:
        print(f"'{name}' is not a valid column name")
    try:
        #set function only keeps unique values
        allDesc = list(set(df[desc].to_numpy()))
        descNames, descLocations = extractNamesFromDescriptions(allDesc)
        print(descNames)
        print(descLocations)
    except:
        print(f"'{name}' is not a valid column name")
    try:
        allLoca = df[loca].to_numpy()
        #input a search function here to compare against add.csv
    except:
        print(f"'{name}' is not a valid column name")
    
    return allNames, descNames, descLocations, allLoca

#//--------------------------------------------------------------------------------------------------------------------------------------

#? Routes for Website
#boostrap test
@app.route('/bootsrap', methods = ['GET', 'POST'])
def base():
    return render_template("base.html", )


#route to search individual name
@app.route('/', methods = ['GET', 'POST'])
def home():
    form = SanctionSearch()
    if form.is_submitted():
        result = request.form
        high_scores, flag = searchSanction(result["nameToSearch"])
        return render_template("searchResult.html", result=result, high_scores = high_scores, flag=flag)
    return render_template("home.html", form=form)

#shows a list of sanction names
@app.route('/sanctionList')
def importSanctionList():
    return render_template("allSanctioned.html", names = readSanctionList())

#shows a list of sanction names
@app.route('/displacy')
def displacyTest():
    text = "When Sebastian Thrun started working on self-driving cars at Google in 2007, few people outside of the company took him seriously."
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    html = displacy.render(doc, style="ent", page=False)
    print(type(html))
    return html

#accepts excel file upload and returns sanction search on values in the uploaded file
@app.route('/excel', methods = ['GET', 'POST'])
def searchAllExcel():
    form = ExcelUploadWithLabels()

    if form.is_submitted():
        result = request.form
        excelUpload = form.upload.data
        df = pd.read_excel(excelUpload, result["sheetName"])
        allNames, descNames, descLocations, allLocations = readMultipleExcelColumns(df, result["name"], result["desc"], result["loca"])
        namesResult = searchSanctionMany(allNames)
        descNamesResult = searchSanctionMany(descNames)
        return render_template("excelSearchResult.html", namesResult = namesResult, descNamesResult = descNamesResult)
    return render_template("excelUpload.html", form=form)

#route to search multiple people - seperates by whitespace
@app.route('/searchText', methods = ['GET', 'POST'])
def searchSanctionText():
    form = SanctionSearchList()

    if form.is_submitted():
        result = request.form
        print(result["textToSearch"].split(" "))
        return render_template("manySearchResult.html", result=result, searchResult = searchSanctionMany(result["textToSearch"].split(" ")))
    return render_template("inputText.html", form=form)

#route to test excel input
@app.route('/excelTest')
def searchExcel():
    return readExcel()
    #return readExcel()


#//--------------------------------------------------------------------------------------------------------------------------------------

#? Code to run app.py

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=True)