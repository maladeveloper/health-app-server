import requests


def returnPatientCholesterolLevel(patientID):
    root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
    search3_url = root_url + "Observation?patient="+patientID+"&code=2093-3&_sort=-date"
    data2 = requests.get(url=search3_url).json()
    ##not all patients might have cholesterol data so we must try-catch
    entry = data2['entry']

    #Since we sorted by newest date, we get the first enty from the entiries array
    cholesterol_details_dict = {}
    #Make sure there is an entry
    if len(entry)>=1:
        cholesterol_details_dict["cholesterol_data"] = str(entry[0]['resource']['valueQuantity']['value'])
        cholesterol_details_dict["cholesterol_units"] = str(entry[0]['resource']['valueQuantity']['unit'])
        cholesterol_details_dict["time_issued"] = str(entry[0]['resource']['issued'])

    return cholesterol_details_dict