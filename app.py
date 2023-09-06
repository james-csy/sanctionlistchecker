from flask import Flask, render_template, request
from thefuzz import fuzz
import csv
import requests
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


#updates OFAC sanctions list:
def updateSanctionList():
    csv_url = "https://www.treasury.gov/ofac/downloads/sdn.csv"
    with requests.Session() as s:
        download = s.get(csv_url)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=",")
        my_list = list(cr)
        names = []
        for row in my_list:
            try:
                names.append(row[1]) #column index 1 contains NAME data
            except:
                pass
        with open('files/sdn.txt', 'w') as f:
            for name in names:
                f.write(name)
                f.write('\n')

def readUpdatedSanctionList():
    with open("files/sdn.txt") as f:
        names = [str(line)[:-1] for line in list(f)]
    return names



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
    for name in readUpdatedSanctionList():
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

#function that extracts names and locations from list of descriptions
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

#function that extracts names and locations from list of descriptions
def extractNamesFromSingleDescription(description):
    locations = []
    names = []
    nlp = spacy.load("en_core_web_sm")
    analyzer = nlp(description)
    for ent in analyzer.ents:
        if ent.label_ in ["Person", "ORG"]:
            names += [ent.text]
        elif ent.label_ == "GPE":
            locations += [ent.text]
    return names, locations

#function to output displacy view and sanction list search scores
def displacyDescription(description):
    nlp = spacy.load("en_core_web_sm")
    analyzer = nlp(description)
    html = displacy.render(analyzer, style="ent", page=False)
    locations = []
    names = []
    for ent in analyzer.ents:
        if ent.label_ in ["PERSON", "ORG"]:
            names += [ent.text]
        elif ent.label_ == "GPE":
            locations += [ent.text]
    return html, names, locations


#take inputs of excel file and names of columns and then perform a sanction search on everything relevant (this function used for /excel)
def readMultipleExcelColumns(df, name = "Insured Name", desc = "Event Description", loca = "Loss Location"):
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

#strictly returns columns of excel file - no additional functions (using this for excel alternative)
def extractExcelColumns(df, name = "Insured Name", desc = "Event Description", loca = "Loss Location"):
    nameColumn = []
    descColumn= []
    locaColumn = []
    try:
        #set function only keeps unique values
        nameColumn = list(set(df[name].to_numpy()))
    except:
        print(f"'{name}' is not a valid column name")
    try:
        #set function only keeps unique values
        descColumn = list(set(df[desc].to_numpy()))
    except:
        print(f"'{name}' is not a valid column name")
    try:
        locaColumn = df[loca].to_numpy()
    except:
        print(f"'{name}' is not a valid column name")
    
    return nameColumn, descColumn, locaColumn

#//--------------------------------------------------------------------------------------------------------------------------------------

#? Routes for Website

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
    return render_template("allSanctioned.html", names = readUpdatedSanctionList())

#displacy library test
@app.route('/update')
def update():
    form = SanctionSearch()
    updateSanctionList()
    return render_template("update.html")


#displacy library test
@app.route('/displacy')
def displacyTest():
    text = "When Sebastian Thrun started working on self-driving cars at Google in 2007, few people outside of the company took him seriously."
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    html = displacy.render(doc, style="ent", page=False)
    print(type(html))
    return html

#route to search multiple people - seperates by whitespace
@app.route('/searchText', methods = ['GET', 'POST'])
def searchSanctionText():
    form = SanctionSearchList()

    if form.is_submitted():
        result = request.form
        html, names, locations = displacyDescription(result["textToSearch"])
        allToSearch = names + locations
        return render_template("manySearchResult.html", result=result, searchResult = searchSanctionMany(allToSearch), html=html)
    return render_template("inputText.html", form=form)


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

#excel but with displacy view for each description
# create dictionary (Insured Name is primary key)
# excel["Company Name"]["descriptions"] = ["description 1", "description 2", "description 3"]
# excel["Company Name"]["flag"] = True/False
# excel["Company Name"]["descriptionFlag"] = True/False

@app.route('/excelAlternate')
def excelAlternate():
    form = ExcelUploadWithLabels()

    if form.is_submitted():
        result = request.form
        excelUpload = form.upload.data
        df = pd.read_excel(excelUpload, result["sheetName"])
        names, descriptions, locations = extractExcelColumns(df)
        organizedData = {}
        for i in range(len(names)):
            if names[i] not in organizedData:
                organizedData[names[i]] = {"claims": [
                    {"row":i,
                     "description": descriptions[i],
                     "location": locations[i]
                     }],
                     "nameFlagged": [searchSanction(names[i])]
                     }
            else:
                organizedData[names[i]]["claims"].append({"d": descriptions[i], "l": locations[i]})
            
                
            
        allNames, descNames, descLocations, allLocations = readMultipleExcelColumns(df, result["name"], result["desc"], result["loca"])
        namesResult = searchSanctionMany(allNames)
        descNamesResult = searchSanctionMany(descNames)
        return render_template("excelSearchResult.html", namesResult = namesResult, descNamesResult = descNamesResult)
    return render_template("excelUpload.html", form=form)

    return readExcel()
    #return readExcel()


#//--------------------------------------------------------------------------------------------------------------------------------------

#? Code to run app.py

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=False)