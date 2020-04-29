from flask import Flask, request
from flask import jsonify
import requests
import functions

app = Flask(__name__)


@app.route('/hi')
def hello():
    return "Hello World!"

@app.route('/associatedPatients')
def returnAssociatedPatients():
    #get the practitioner id
    prac_id = request.args.get('pracid')
    print(prac_id)

    if prac_id==None:
        ##just assign a defualt id so the system doesnt break
        prac_id = 3

    #Pass the practitioner to the function that returns the array of patient IDs
    patientIDArray = functions.returnPatientIDArray(str(prac_id))

    ###NOW I CAN SEARCH THROUGH ALL THE EnCOUNTERS
    array_dict = {"array":patientIDArray}

    return jsonify(array_dict)


if __name__ == '__main__':
    app.run()