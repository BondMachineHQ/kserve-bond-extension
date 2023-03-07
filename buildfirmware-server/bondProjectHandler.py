from strategies.bmNNProjectHandler import BMNeuralNetworkProjectHandler

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
    
    def buildProject(self):
        if self.request.projectType == "neuralnetwork":
            bmNeuralNetworkProjectHandler = BMNeuralNetworkProjectHandler(self.request)
            bmNeuralNetworkProjectHandler.build()
            bmNeuralNetworkProjectHandler.exec()
        else:
            raise Exception("Project type not handled")
        
        
    def startFirmwareGeneration(self):
        print("Start firmware generation")