import requests
import pprint

root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
search1_url = root_url + "/Practitioner?identifier=93520"
data = requests.get(url=search1_url).json()
pprint.pprint(data)
