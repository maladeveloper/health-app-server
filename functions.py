from threading import Thread

import requests

def getAllPractitionerObjIDs(prac_identifier,prac_lname):
    root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
    search1_url = root_url + "/Practitioner?identifier="+prac_identifier
    data = requests.get(url=search1_url).json()
    allPractitionerIDs = []
    # Now search all the encounters and append patient IDs to patient ID array
    next_page = True
    next_url = search1_url
    count_page = 0
    count_id = 0
    count_encounters = 0
    while next_page:
        data = requests.get(url=next_url).json()


        # As discussed before, The monash FHIR server return results in a series of pages.
        # Each page contains 10 results as default.
        # here we check and record the next page
        next_page = False
        links = data['link']
        for i in range(len(links)):
            link = links[i]
            if link['relation'] == 'next':
                next_page = True
                next_url = link['url']
                count_page += 1

        for practitionerObj in data["entry"]:
            """
              Since there can be more than on practiitoner with the same Identifier (BUG ALDEIDA MENTIONED)
              we must check the names are the same
              """
            if practitionerObj['resource']['name'][0]['family'] == prac_lname:
                count_id+=1
                allPractitionerIDs.append(practitionerObj['resource']['id'])
                print("anotherID"+str(count_id))

        print(allPractitionerIDs)
        print(count_page)

    return allPractitionerIDs


def returnPatientData(prac_ID,patientIDArray):
    root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
    search1_url = root_url + "Encounter?practitioner=" + str(prac_ID)

    #Now search all the encounters and append patient IDs to patient ID array
    next_page = True
    next_url = search1_url
    count_page = 0
    count_patient = 0
    count_encounters = 0

    while next_page:
        dReports = requests.get(url=next_url).json()

        next_page = False
        links = dReports['link']
        for i in range(len(links)):
            link = links[i]
            if link['relation'] == 'next':
                next_page = True
                next_url = link['url']
                count_page += 1

        # Extract data
        entry = dReports['entry']
        for i in range(len(entry)):
            count_encounters+=1
            patientID = entry[i]['resource']['subject']['reference'].split('/')[1]
            patientIDArray.add(patientID)
    return

class GetPatientDataWorker(Thread):

    def __init__(self, queue,patientIDArray):
        Thread.__init__(self)
        self.queue = queue
        self.patientIDArray =patientIDArray

    def run(self, ):
        while True:
            # Get the work from the queue and expand the tuple
            practitionerID = self.queue.get()
            try:
                returnPatientData(practitionerID,self.patientIDArray)
            finally:

                self.queue.task_done()