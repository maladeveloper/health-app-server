from threading import Thread

import requests


def returnNUllCholesterolData(patientID):
    cholesterol_details_dict = {}
    cholesterol_details_dict["cholesterol_data"] = "NONE"
    cholesterol_details_dict["cholesterol_units"] = "NONE"
    cholesterol_details_dict["time_issued"] = "NONE"
    cholesterol_details_dict['ID'] = patientID
    return cholesterol_details_dict

def returnPatientCholesterolLevel(patientID,patientsCholesterolData):
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
        cholesterol_details_dict["time_issued"] = str(entry[0]['resource']['issued'])
        cholesterol_details_dict['ID'] = patientID
    else:
        return

    patientsCholesterolData.append( cholesterol_details_dict)
    return

class GetPatientCholesterolDataWorker(Thread):

    def __init__(self, queue,patientsCholesterolData):
        Thread.__init__(self)
        self.queue = queue
        self.patientsCholesterolData =patientsCholesterolData

    def run(self, ):
        while True:
            # Get the work from the queue and expand the tuple
            patientID = self.queue.get()
            try:
                returnPatientCholesterolLevel(patientID,self.patientsCholesterolData)
            finally:

                self.queue.task_done()