import requests

def getAndVerifyPractitioner(prac_identifier):
    root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
    search1_url = root_url + "/Practitioner?identifier="+prac_identifier
    data = requests.get(url=search1_url).json()
    practitionerObj = {}

    def returnNullPractitioner():
        practitionerObj["fname"] = "NONE"
        practitionerObj['lname'] = "NONE"
        practitionerObj["prefix"] = "NONE"
        practitionerObj["identifier"] = prac_identifier
        return practitionerObj



    ##If there exists no practioner, then return null practitioner object
    try:
        entries = data['entry']
    except KeyError:
        return returnNullPractitioner()

    """
     Since there can be more than on practiitoner with the same Identifier (BUG ALDEIDA MENTIONED)
     we choose the details of the first entry and choose that as the practitioner for this identifier
     """
    #Otherwise get the practitioner details of the first entry
    if len(entries)>=1:
        name = entries[0]['resource']['name'][0]
        practitionerObj["prefix"] = name['prefix'][0]
        practitionerObj["fname"] = name['given'][0]
        practitionerObj["lname"] = name['family']
        practitionerObj['fullname'] = name['prefix'][0]+name['given'][0]+" "+name['family']
        practitionerObj["identifier"] = prac_identifier
    else:
        return returnNullPractitioner()
    return practitionerObj








