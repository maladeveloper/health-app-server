from queue import Queue
from threading import Thread

import requests


def returnNUllCholesterolData(patientID):
    cholesterol_details_dict = {}
    cholesterol_details_dict["cholesterol_data"] = "NONE"
    cholesterol_details_dict["cholesterol_units"] = "NONE"
    cholesterol_details_dict["time_issued"] = "NONE"
    cholesterol_details_dict['ID'] = patientID
    return cholesterol_details_dict

def returnPatientCholesterolLevel(patientID,patientsData):
    cholesterol_details_dict = {}
    root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
    search3_url = root_url + "Observation?patient="+patientID+"&code=2093-3&_sort=-date"
    data = requests.get(url=search3_url)

    ##not all patients might have cholesterol data so we must error check
    if data.status_code!=200:
        return

    data2 = data.json()

    ## Some returned data might not be in the form of an observation but rather a bundle containing nothing
    try:
        entry = data2['entry']
    except KeyError:
        return

    #Since we sorted by newest date, we get the first enty from the entiries array

    #Make sure there is an entry
    if len(entry)>=1:
        cholesterol_details_dict["cholesterol_data"] = str(entry[0]['resource']['valueQuantity']['value'])
        cholesterol_details_dict["cholesterol_units"] = str(entry[0]['resource']['valueQuantity']['unit'])
        cholesterol_details_dict["cholesterol_timeIssued"] = str(entry[0]['resource']['issued'])
        cholesterol_details_dict['ID'] = patientID
    else:
        return

    patientsData.append( cholesterol_details_dict)
    return


def returnPatientBloodPressureLevel(patientID,patientsData):
    bloodPressure_dict = {}
    root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
    search3_url = root_url + "Observation?patient=" + patientID + "&code=55284-4&_sort=-date"
    data = requests.get(url=search3_url)
    ##not all patients might have cholesterol data so we must error check
    if data.status_code != 200:
        return

    data2 = data.json()

    ## Some returned data might not be in the form of an observation but rather a bundle containing nothing
    try:
        entry = data2['entry'][0]
    except KeyError:
        return


    # Need to define a new code for each component of the blood pressure
    components = entry['resource']['component']
    for component in components:
        #Get the value from the component
        name = component["code"]['coding'][0]['display']
        name = name.replace(" ", "")
        value = component['valueQuantity']['value']

        #Get the units of the component
        unitName = name+"_units"
        units = component['valueQuantity']['unit']

        #Get the issued time of the measurement
        issuedTimeName = name + "_timeIssued"
        issuedTime = entry['resource']['issued']

        #Add the acquired information to the dictionary
        bloodPressure_dict[name] = value
        bloodPressure_dict[unitName] = units
        bloodPressure_dict[issuedTimeName] = issuedTime

    bloodPressure_dict['ID'] = patientID


    #Add the final values into all data array.
    patientsData.append(bloodPressure_dict)
    return



class GetPatientDataWorker(Thread):

    def __init__(self, queue,patientsData, dataFunction):
        Thread.__init__(self)
        self.dataFunction = dataFunction
        self.queue = queue
        self.patientsData =patientsData

    def run(self, ):
        while True:
            # Get the work from the queue and expand the tuple
            patientID = self.queue.get()
            try:
                self.dataFunction(patientID, self.patientsData)
            finally:

                self.queue.task_done()



def findPatientData(dataSpecifier,patientIDArray, ALL_DATA):


    # Create a queue to communicate with the worker threads
    queue = Queue()

    # Create 32 worker threads
    THREADS = 32


    if dataSpecifier == "cholesterol":

        for x in range(THREADS):
            worker = GetPatientDataWorker(queue, ALL_DATA,returnPatientCholesterolLevel)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()

        for patID in patientIDArray:
            print(patID)
            queue.put(str(patID))
        # Causes the main thread to wait for the queue to finish processing all the tasks
        queue.join()

    elif dataSpecifier =="bloodPressure":
        for x in range(THREADS):
            worker = GetPatientDataWorker(queue, ALL_DATA, returnPatientBloodPressureLevel)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()

        for patID in patientIDArray:
            print(patID)
            queue.put(str(patID))
            # Causes the main thread to wait for the queue to finish processing all the tasks
        queue.join()



def collateAllData(All_DATA):

    #The new array that contains all the patient data
    NewAllData = dict()
    for data in All_DATA:
        try:
            NewAllData[data["ID"]].update(data)

        except KeyError:
            NewAllData[data["ID"]] = dict()
            # Now update the dictionary to contain the specified data
            NewAllData[data["ID"]].update(data)

    return NewAllData.values()
