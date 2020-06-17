from queue import Queue
from threading import Thread
import json
import requests




def returnPatientLevel(patientID,patientsData,dataResource):
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
    #A for loop that runs for the number of historical data is needed
    for i in range(dataResource['history']):
        observation_details_dict = {}

        appendage = '_'+str(i)


        #The entry index is specified by how recently in history the data is
        entryIndex = i

        try:

            observation_details_dict[dataResource['name']+"_data"+appendage] = str(entry[entryIndex]['resource']['valueQuantity']['value'])
            observation_details_dict[dataResource['name']+"_units"] = str(entry[entryIndex]['resource']['valueQuantity']['unit'])
            observation_details_dict[dataResource['name']+"_timeIssued"+appendage] = str(entry[entryIndex]['resource']['issued'])
            observation_details_dict['ID'] = patientID
        except :
            ##This would be because there is no entry for this specific index
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
    #A for loop that runs for the number of historical data is needed
    for i in range(dataResource['history']):
        observation_details_dict = {}

        appendage = '_'+str(i)


        #The entry index is specified by how recently in history the data is
        entryIndex = i
        try:
            entry = data2['entry'][entryIndex]
        except :
            #We can exit the function here because if there is no entryIndex, there is no value for any index higher
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
                bloodPressure_dict[dataResource['name']+"_data"+appendage] = str(component['valueQuantity']['value'])
                bloodPressure_dict[dataResource['name']+"_units"] = str(component['valueQuantity']['unit'])
                bloodPressure_dict[dataResource['name']+"_timeIssued"+appendage] = str(entry['resource']['issued'])


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
                self.dataFunction(patientID, self.patientsData,self.dataResource,)
            finally:

                self.queue.task_done()



def findPatientData(dataSpecifier,patientIDArray, ALL_DATA):


    # Create a queue to communicate with the worker threads
    queue = Queue()

    # Create 32 worker threads
    THREADS = 16


    observationToCodeMap = {
                              "cholesterol": "2093-3",
                              "systolic_blood_pressure": "55284-4",
                              "diastolic_blood_pressure": "55284-4"
                           }

    #Combine the data specifier string and the data code into a data resource dictionary
    dataResource = {}
    dataResource['name'] = dataSpecifier[0]
    dataResource['code'] = observationToCodeMap[dataSpecifier[0]]
    dataResource['history'] = dataSpecifier[1]


    #for the normal case of only finding the latest dataset no appendage is needed
    if dataResource['code'] =="55284-4":
        for x in range(THREADS):
            worker = GetPatientDataWorker(queue, ALL_DATA, returnPatientBloodPressureLevel,dataResource)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()

        for patID in patientIDArray:
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
