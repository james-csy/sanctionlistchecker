from flask import Flask, render_template, request
from thefuzz import fuzz
import csv
from forms import SanctionSearch


app = Flask(__name__)
app.config['SECRET_KEY'] = "sanctionsearch"

#extracts names from sanction lists and outputs list of names
def readSanctionList():
        with open('files/sdn.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            names = []
            for row in csv_reader:
                names.append(row["NAME"])
            #print(f'Processed {line_count} lines.')
        return names


#return names with the highest partial_ratio score
def searchSanction(nameToSearch):
    scores = {}
    high_scores = {}
    for name in readSanctionList():
         try:
            scores[str(name)] = fuzz.partial_ratio(name, nameToSearch)
            if scores[str(name)] >= 80:
                high_scores[str(name)] = scores[str(name)]
         except:
            scores[str(name)] = 0
    return dict(sorted(high_scores.items(), key=lambda item: item[1], reverse=True))

@app.route('/')
def importSanctionList():
    return readSanctionList()

@app.route('/searchName', methods = ['GET', 'POST'])
def searchSanctionList():
    form = SanctionSearch()
    if form.is_submitted():
        result = request.form
        high_scores = searchSanction(result["nameToSearch"])
        return render_template("searchResult.html", result=result, high_scores = high_scores)
    return render_template("inputName.html", form=form)



if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=True)