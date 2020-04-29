from flask import Flask
from flask import jsonify
import requests
import functions

app = Flask(__name__)


@app.route('/hi')
def hello():
    return "Hello World!"

@app.route('/associatedPatients')
def returnAssociatedPatients():
    ##Just testing to see if i can make these kinds of API requests anyway

    patientIDArray = functions.returnPatientIDArray(str(5059914))
    ###NOW I CAN SEARCH THROUGH ALL THE EnCOUNTERS
    array_dict = {"array":patientIDArray}

    return jsonify(array_dict)


if __name__ == '__main__':
    app.run()