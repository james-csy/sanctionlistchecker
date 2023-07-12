from flask import Flask
import csv

app = Flask(__name__)


@app.route('/')
def hello():


    def readSanctionList():
        with open('files/sdn.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                print(row)
                line_count += 1
                if line_count == 20:
                    break
            print(f'Processed {line_count} lines.')
    readSanctionList()
    
    return '<h1>Check your files for mentions of People/Companies on the US Sanctions List</h1>'
