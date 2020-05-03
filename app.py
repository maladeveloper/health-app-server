from queue import Queue
from functions import GetPatientDataWorker
from patientDetailFunctions import GetPatientCholesterolDataWorker
from flask import Flask, request
from flask import jsonify
import requests
import functions
from ast import literal_eval
import patientDetailFunctions
import verificationFunctions
app = Flask(__name__)


@app.route('/hi')
def hello():
    return "Hello World!"

@app.route('/associatedPatients')
def getAssociatedPatients():
    #get the practitioner id from the url argument pracid
    prac_id = request.args.get('pracid')
    prac_lname = request.args.get('praclname')
    if prac_id==None:
        ##just assign a defualt id so the system doesnt break
        prac_id = 3

    #Find all the practitioner IDs
    practitionerIDs = functions.getAllPractitionerObjIDs(str(prac_id),str(prac_lname))

    ##Set to store all the patient IDS ALL threads share this
    patientIDArray=set()

    # Create a queue to communicate with the worker threads
    queue = Queue()

    # Create 16 worker threads
    THREADS=20
    for x in range(THREADS):
        worker = GetPatientDataWorker(queue,patientIDArray)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    for practitionerID in practitionerIDs:
        queue.put(practitionerID)

    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()

    #Put the patients ID Array into a dictionary to zip
    array_dict = {"array":list(patientIDArray)}

    return jsonify(array_dict)

@app.route('/patientDataCholesterol')
def getPatientDetails():
    patientIDArray = literal_eval(request.args.get("patientidarray"))



    ##Set to store all the patient Cholesterol data ALL threads share this
    patientsCholesterolData=[]

    # Create a queue to communicate with the worker threads
    queue = Queue()

    # Create 4 worker threads
    THREADS = 20
    for x in range(THREADS):
        worker = GetPatientCholesterolDataWorker(queue, patientsCholesterolData)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    for patID in patientIDArray:
        print(patID)
        queue.put(str(patID))

    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()


    array_dict = {"array":list(patientsCholesterolData)}

    return jsonify(array_dict)


@app.route('/getPractitioner')
def verifyAndReturnPractitioner():
    prac_id = request.args.get('pracid')
    #DEfault the id to something ##REMOVE LATER
    if prac_id==None:
        prac_id = "93520"
    return jsonify(verificationFunctions.getAndVerifyPractitioner(str(prac_id)))


if __name__ == '__main__':
    app.run()