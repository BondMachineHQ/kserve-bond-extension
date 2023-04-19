import buildfirmware_pb2
import buildfirmware_pb2_grpc
import grpc
import uuid
import string
import random
from utils import PrintHandler

class BuildFirmwareHandler(object):
    
    _instance = None
    _channel = None
    _stub = None
    
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
    
    def initialize(self):
        if self._channel == None:
            self._channel = grpc.insecure_channel('10.2.129.49:50051')
            self._stub = buildfirmware_pb2_grpc.BuildFirmwareServerStub(self._channel)
        
    def generate_random_name(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))   
        
    def generateJob(self, hlsToolkit, targetBoard, projectType, nInputs, nOutputs, flavor, sourceNeuralNetwork):
        
        self.initialize()
        
        job = buildfirmware_pb2.BuildFirmwareRequest(
        uuid = str(uuid.uuid4()),
        projectName = self.generate_random_name(8),
        hlsToolkit = hlsToolkit,
        targetBoard = targetBoard,
        projectType = projectType,
        nInputs = nInputs,
        nOutputs = nOutputs,
        flavor = flavor,
        sourceNeuralNetwork = sourceNeuralNetwork)
        
        response_iterator = self._stub.buildFirmware(job)
        firmware_name = ""
        for response in response_iterator:
            firmware_name = response.message
            PrintHandler().print_success(response.message)
        
        return firmware_name
    