from flask import Flask, render_template
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

@app.route('/')
def importSanctionList():
    return readSanctionList()

@app.route('/search')
def searchSanction():
    scores = {}
    high_scores = {}
    for name in readSanctionList():
         try:
            scores[str(name)] = fuzz.partial_ratio(name, "VINALES")
            if scores[str(name)] > 80:
                high_scores[str(name)] = scores[str(name)]
         except:
            scores[str(name)] = 0
    return high_scores

@app.route('/searchName')
def searchSanctionList():
    form = SanctionSearch()
    return render_template("search.html", form=form)



if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=True)