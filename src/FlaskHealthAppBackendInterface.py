from abc import ABCMeta, abstractmethod
from flask_classful import FlaskView, route

class FlaskHealthAppBackendInterface(FlaskView):

    @abstractmethod
    def getAssociatedPatients(self): raise NotImplementedError

    @abstractmethod
    def getPatientDetails(self):NotImplementedError

    @abstractmethod
    def verifyAndReturnPractitioner(self):NotImplementedError