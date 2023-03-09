import subprocess
import os
import requests
from google_drive_downloader import GoogleDriveDownloader as gdd

class BMNeuralNetworkProjectHandler():
    
    def __init__(self, request):
        self.request = request
        self.projectType = "neural_network"
        self.projectName = ""
        self.targetBoard = ""
        self.nInputs = 0
        self.nOutputs = 0
        self.neuralNetwork = ""
        self.flavor = ""
        self.cmdsToExec = ["bondmachine", "hdl", "design_synthesis", "design_implementation", "design_bitstream"]
        self.check()
                
    def check(self):
        if self.request.nInputs == None:
            raise Exception("nInputs is required for neural network project")
        
        if self.request.nOutputs == None:
            raise Exception("nOutputs is required for neural network project")
        
        if self.request.sourceNeuralNetwork == None:
            raise Exception("source neural networks is required for neural network project")
        
        if self.request.flavor == None:
            raise Exception("flavor (aximm or axist) is required for neural network project")
        
        self.projectName = self.request.projectName
        self.targetBoard = self.request.targetBoard
        self.nInputs = self.request.nInputs
        self.nOutputs = self.request.nOutputs
        self.neuralNetwork = self.request.sourceNeuralNetwork
        self.flavor = self.request.flavor
        
    def build(self):
        
        # create the target project directory with the uuid of the job
        try:
            subprocess.check_output(f'mkdir {self.request.uuid}', shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Command failed with exit code {e.returncode}") from e
        
        # create the bondmachine project using the bmhelper tool
        cmdToExec = f'cd {self.request.uuid} && bmhelper create --project_name {self.projectName} --board {self.targetBoard} --project_type {self.projectType} --n_inputs {self.nInputs} --n_outputs {self.nOutputs} --source_neuralbond {self.neuralNetwork} --flavor {self.flavor}'
        try:
            output = subprocess.check_output(cmdToExec, shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Command failed with exit code {e.returncode}") from e
        
        ########################### WIP ###########################
        ##### DOWNLOAD OF THE FILE FROM GDRIVE IS NOT CORRECT #####
        # here download the .json description file of the neural network from endpoint
        # https://drive.google.com/file/d/1Duhcy6mGeXWR3exDVe5o0KsLDwuS7LfP/view?usp=share_link
        
        gdd.download_file_from_google_drive(file_id='1Duhcy6mGeXWR3exDVe5o0KsLDwuS7LfP', dest_path=f'{os.getcwd()}/{self.request.uuid}/{self.projectName}/banknote.json', unzip=False, showsize=False)
        
        ###########################################################        
        return self.cmdsToExec
    
    def exec(self, command):
                
        cmdToExec = f'cd {self.request.uuid}/{self.projectName} && make '+command
        
        try:
            subprocess.check_output(cmdToExec, shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Command failed with exit code {e.returncode}") from e