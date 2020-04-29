from flask import Flask
from flask import jsonify
import requests

app = Flask(__name__)


@app.route('/hi')
def hello():
    return "Hello World!"

@app.route('/example')
def example():
    ##Just testing to see if i can make these kinds of API requests anyway
    root_url = 'https://fhir.monash.edu/hapi-fhir-jpaserver/fhir/'
    patients_url = root_url + "Patient"
    patient_id_url = patients_url + "/1"
    data = requests.get(url=patient_id_url).json()
    return data

if __name__ == '__main__':
    app.run()