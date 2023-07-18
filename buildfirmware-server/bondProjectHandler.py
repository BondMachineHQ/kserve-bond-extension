from strategies.bmNNProjectHandler import BMNeuralNetworkProjectHandler
import buildfirmware_pb2

class BondMachineProjectHandler:
    
    def __init__(self, request):
        self.request = request
    
    def checkRequirements(self):
        projectName = self.request.projectName
        if projectName == None:
            raise Exception("project name is required")
        
        targetBoard = self.request.targetBoard
        if targetBoard == None:
            raise Exception("targetBoard is required")
            
        projectType = self.request.projectType
        if projectType == None:
            raise Exception("projectType is required")
    
    def build(self):
        if self.request.projectType == "neuralnetwork":
            bmNeuralNetworkProjectHandler = BMNeuralNetworkProjectHandler(self.request)
            return bmNeuralNetworkProjectHandler.build()
        else:
            raise Exception("Project type not handled")
        
    def exec(self, cmd):
        if self.request.projectType == "neuralnetwork":
            bmNeuralNetworkProjectHandler = BMNeuralNetworkProjectHandler(self.request)
            bmNeuralNetworkProjectHandler.exec(cmd)
        else:
            raise Exception("Project type not handled")