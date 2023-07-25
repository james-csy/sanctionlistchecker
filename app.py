from flask import Flask, render_template, request
from thefuzz import fuzz
import csv
from forms import SanctionSearch, SanctionSearchList

#import for excel file handling
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np

#import openpyxl




app = Flask(__name__)
app.config['SECRET_KEY'] = "sanctionsearch"

#define whitelist
with open("files/whitelist.txt") as f:
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
    for i in name.split(" "):
        if i not in whitelist:
            result += (i + " ")
    return result

#return names with the highest partial_ratio score
def searchSanction(nameToSearch):
    upperName = nameToSearch.upper()
    print(upperName)
    scores = {}
    high_scores = {}
    flag = False
    for name in readSanctionList():
         try:
            scores[str(name)] = fuzz.token_set_ratio(name, removeCommon(upperName))
            if scores[str(name)] >= 80:
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

def writeExcel(df, path):
    with pd.ExcelWriter(path, mode = 'a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name="Sheet2")
    return "Success"

def readExcel():
    df = pd.read_excel(r'files/searchNames.xlsx')
    
    #print(type(df["Name"]))
    searchResult = searchSanctionMany(df["Name"].to_numpy())
    toExcel = pd.DataFrame(searchResult).T
    writeExcel(toExcel, "files/searchNames.xlsx")
    return render_template("excelSearchResult.html", searchResult = searchResult)



@app.route('/')
def importSanctionList():
    return render_template("allSanctioned.html", names = readSanctionList())

#route to search individual name
@app.route('/searchName', methods = ['GET', 'POST'])
def searchSanctionList():
    form = SanctionSearch()
    if form.is_submitted():
        result = request.form
        high_scores, flag = searchSanction(result["nameToSearch"])
        return render_template("searchResult.html", result=result, high_scores = high_scores, flag=flag)
    return render_template("inputName.html", form=form)


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
@app.route('/excel')
def searchExcel():
    return readExcel()
    #return readExcel()



if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=True)