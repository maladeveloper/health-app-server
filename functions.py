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


def returnPatientIDArray(prac_identifier,prac_lname):
    patientIDArray = set()
    ##For all the IDs each practitioner has, we must search all encounters by it
    for prac_ID in getAllPractitionerObjIDs(prac_identifier,prac_lname):
        root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
        search1_url = root_url + "Encounter?practitioner=" + str(prac_ID)
        #The patient set that stores all the patients



        #Now search all the encounters and append patient IDs to patient ID array
        next_page = True
        next_url = search1_url
        count_page = 0
        count_patient = 0
        count_encounters = 0

        while next_page:
            dReports = requests.get(url=next_url).json()

            # As discussed before, The monash FHIR server return results in a series of pages.
            # Each page contains 10 results as default.
            # here we check and record the next page
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
                prac_returned_id =str(entry[i]['resource']['participant'][0]['individual']['reference'].split('/')[1])
                ##print("PAGE: "+str(count_page))
                ##print("ENCOUNT:"+str(count_encounters))
                #Get the patient ID from such an entry
                patientID = entry[i]['resource']['subject']['reference'].split('/')[1]
                #print(patientID)
                patientIDArray.add(patientID)

    return list(patientIDArray)

