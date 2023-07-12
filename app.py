from flask import Flask
import csv

app = Flask(__name__)


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
def SearchSanctionList():
    inSanctionList = False
    return str(inSanctionList)


if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=True)
