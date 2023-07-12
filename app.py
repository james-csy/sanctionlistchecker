from flask import Flask
import csv

app = Flask(__name__)


@app.route('/')
def importSanctionList():
    def readSanctionList():
        with open('files/sdn.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            names = []
            for row in csv_reader:
                names.append(row["NAME"])
            #print(f'Processed {line_count} lines.')
        return names
    sanctionedNames = readSanctionList()

    return sanctionedNames

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=True)
