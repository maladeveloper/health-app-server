import ast

from flask import jsonify
from flask_classful import route
from ast import literal_eval
from queue import Queue
from src import getPatientDetails_Functions, getAssociatedPatients_Functions, verifyAndReturnPractitioner_Functions
from flask import request
from src.FlaskHealthAppBackendInterface import FlaskHealthAppBackendInterface


class FlaskHealthAppBackend(FlaskHealthAppBackendInterface):

    @route('/associatedPatients')
    def getAssociatedPatients(self):
        #get the practitioner id from the url argument pracid
        prac_id = request.args.get('pracid')
        prac_lname = request.args.get('praclname')


        #Find all the practitioner IDs
        practitionerIDs = getAssociatedPatients_Functions.getAllPractitionerObjIDs(str(prac_id), str(prac_lname))

        ##Set to store all the patient IDS ALL threads share this
        patientIDArray=set()

        # Create a queue to communicate with the worker threads
        queue = Queue()

        # Create 32 worker threads
        THREADS=32
        for x in range(THREADS):
            worker = getAssociatedPatients_Functions.GetPatientDataWorker(queue, patientIDArray)
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

    @route('/patientData')
    def getPatientDetails(self):
        patientIDArray = literal_eval(request.args.get("patientidarray"))
        print(patientIDArray)
        dataSpecifierArray = ast.literal_eval( request.args.get("dataArray"))
        print(dataSpecifierArray)

        ALL_DATA = []

        #Go through all the conditions that are listed in the array.
        for dataSpecifier in dataSpecifierArray:
            getPatientDetails_Functions.findPatientData(dataSpecifier, patientIDArray, ALL_DATA)

        ALL_DATA = getPatientDetails_Functions.collateAllData(ALL_DATA)

        array_dict = {"array":list(ALL_DATA)}

        return jsonify(array_dict)


    @route('/getPractitioner')
    def verifyAndReturnPractitioner(self):
        prac_id = request.args.get('pracid')

        return jsonify(verifyAndReturnPractitioner_Functions.getAndVerifyPractitioner(str(prac_id)))
