import requests


def returnPatientCholesterolLevel(patientID):
    cholesterol_details_dict = {}
    def returnNUllCholesterolData():
        cholesterol_details_dict["cholesterol_data"] = "NONE"
        cholesterol_details_dict["cholesterol_units"]= "NONE"
        cholesterol_details_dict["time_issued"]= "NONE"
        return cholesterol_details_dict

    root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
    search3_url = root_url + "Observation?patient="+patientID+"&code=2093-3&_sort=-date"
    data = requests.get(url=search3_url)
    ##not all patients might have cholesterol data so we must error check
    print(data.status_code)
    if data.status_code!="200":
        return returnNUllCholesterolData()

    data2 = data.json()

    entry = data2['entry']

    #Since we sorted by newest date, we get the first enty from the entiries array

    #Make sure there is an entry
    if len(entry)>=1:
        cholesterol_details_dict["cholesterol_data"] = str(entry[0]['resource']['valueQuantity']['value'])
        cholesterol_details_dict["cholesterol_units"] = str(entry[0]['resource']['valueQuantity']['unit'])
        cholesterol_details_dict["time_issued"] = str(entry[0]['resource']['issued'])
    else:
        return returnNUllCholesterolData()

    return cholesterol_details_dict