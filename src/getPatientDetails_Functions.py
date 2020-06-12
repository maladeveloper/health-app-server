from queue import Queue
from threading import Thread
import json
import requests




def returnPatientLevel(patientID,patientsData,dataResource):
    observation_details_dict = {}
    root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
    search3_url = root_url + "Observation?patient="+patientID+"&code="+ dataResource['code'] +"&_sort=-date"
    data = requests.get(url=search3_url)

    ##not all patients might have the data so we must error check
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
        observation_details_dict[dataResource['name']+"_data"] = str(entry[0]['resource']['valueQuantity']['value'])
        observation_details_dict[dataResource['name']+"_units"] = str(entry[0]['resource']['valueQuantity']['unit'])
        observation_details_dict[dataResource['name']+"_timeIssued"] = str(entry[0]['resource']['issued'])
        observation_details_dict['ID'] = patientID
    else:
        return

    patientsData.append(observation_details_dict)
    return


def returnPatientBloodPressureLevel(patientID,patientsData, dataResource):
    bloodPressure_dict = {}
    root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
    search3_url = root_url + "Observation?patient=" + patientID + "&code="+dataResource['code']+"&_sort=-date"
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

    # Here we split off between getting the systolic and diastolic data
    systolicBloodPressureCode = "8480-6"
    diastolicBloodPressureCode = "8462-4"
    code = None
    if dataResource['name'] == 'systolic_blood_pressure':
        code = systolicBloodPressureCode
    elif dataResource['name'] == 'diastolic_blood_pressure':
        code = diastolicBloodPressureCode

    # Need to define a new code for each component of the blood pressure
    components = entry['resource']['component']
    for component in components:
        #Check whether the diastolic of systolic data is needed
        if component["code"]['coding'][0]['code'] == code:
            #Add the acquired information to the dictionary
            bloodPressure_dict[dataResource['name']+"_data"] = component['valueQuantity']['value']
            bloodPressure_dict[dataResource['name']+"_units"] = component['valueQuantity']['unit']
            bloodPressure_dict[dataResource['name']+"_timeIssued"] = entry['resource']['issued']

    bloodPressure_dict['ID'] = patientID


    #Add the final values into all data array.
    patientsData.append(bloodPressure_dict)
    return



class GetPatientDataWorker(Thread):

    def __init__(self, queue,patientsData, dataFunction,dataResource):
        Thread.__init__(self)
        self.dataFunction = dataFunction
        self.queue = queue
        self.patientsData =patientsData
        self.dataResource = dataResource

    def run(self, ):
        while True:
            # Get the work from the queue and expand the tuple
            patientID = self.queue.get()
            try:
                self.dataFunction(patientID, self.patientsData,self.dataResource)
            finally:

                self.queue.task_done()



def findPatientData(dataSpecifier,patientIDArray, ALL_DATA):


    # Create a queue to communicate with the worker threads
    queue = Queue()

    # Create 32 worker threads
    THREADS = 32


    observationToCodeMap = {
                              "cholesterol": "2093-3",
                              "systolic_blood_pressure": "55284-4",
                              "diastolic_blood_pressure": "55284-4"
                           }

    #Combine the data specifier string and the data code into a data resource dictionary
    dataResource = {}
    dataResource['name'] = dataSpecifier
    dataResource['code'] = observationToCodeMap[dataSpecifier]

    #There is a special case for the observation of blood pressure.
    if dataResource['code'] =="55284-4":
        for x in range(THREADS):
            worker = GetPatientDataWorker(queue, ALL_DATA, returnPatientBloodPressureLevel,dataResource)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()

        for patID in patientIDArray:
            print(patID)
            queue.put(str(patID))
            # Causes the main thread to wait for the queue to finish processing all the tasks
        queue.join()

    else:
        for x in range(THREADS):
            worker = GetPatientDataWorker(queue, ALL_DATA,returnPatientLevel,dataResource)
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
