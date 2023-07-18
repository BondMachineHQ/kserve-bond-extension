import hls4ml
import os
import subprocess
from tensorflow.keras.models import load_model
import requests

class HLS4MLProjectHandler:
    
    def __init__(self, request):
        self.request = request
        self.supported_boards = [
            {
                "name": "pynq-z2",
                "part": "xc7z020clg400-1"
            },
            {
                "name": "zcu102",
                "part": "xczu9eg-ffvb1156-2-e"
            },
            {
                "name": "alveo-u50",
                "part": "xcu50-fsvh2104-2-e"
            },
            {
                "name": "alveo-u250",
                "part": "xcu250-figd2104-2L-e"
            },
            {
                "name": "alveo-u200",
                "part": "xcu200-fsgd2104-2-e"
            },
            {
                "name": "alveo-u280",
                "part": "xcu280-fsvh2892-2L-e"
            }
        ]
        self.targetBoard = ""
        self.sourceNeuralNetwork = ""
        self.base_url = "https://minio.131.154.96.26.myip.cloud.infn.it/trained-models/"
        self.vivado_path = '/home/ubuntu/Vivado/2019.2/bin:'
        self.fullSourceNNPath = ""
        self.projectName = ""
        self.boardSpecs = None

        os.environ['PATH'] = self.vivado_path + os.environ['PATH']

    def findBoard(self):

        for board in self.supported_boards:
            if board["name"] == self.targetBoard or board["part"] == self.targetBoard:
                return board
        
        return None

    def checkRequirements(self):

        if self.request.targetBoard == None:
            raise Exception("targetBoard is required")
        
        self.targetBoard = self.request.targetBoard

        self.boardSpecs = self.findBoard()
        if self.boardSpecs == None:
            raise Exception("targetBoard requested is not supported by HLS4ML")
        
        if self.request.sourceNeuralNetwork == None:
            raise Exception("source neural network (.h5 file) is necessary")

        if self.request.projectName == None:
            raise Exception("project name is necessary")

        self.projectName = self.request.projectName
        self.sourceNeuralNetwork = self.request.sourceNeuralNetwork

        # create the master directory with the uuid of the request
        try:
            subprocess.check_output(f'mkdir {self.request.uuid}', shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Command failed with exit code {e.returncode}") from e

        # create the project directory inside the master directory
        try:
            subprocess.check_output(f'mkdir {self.request.uuid}/{self.projectName}', shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Command failed with exit code {e.returncode}") from e

        # download the .h5 file from minio
        try:
            endpoint_url = self.base_url + self.sourceNeuralNetwork
            response = requests.get(endpoint_url)
            self.fullSourceNNPath = f'{os.getcwd()}/{self.request.uuid}/{self.projectName}/'+self.sourceNeuralNetwork
            
            open(self.fullSourceNNPath, "wb").write(response.content)
        except Exception as e:
            raise Exception("Error during download of .h5 neural network model "+str(e))

        # load the model
        self.model = load_model(self.fullSourceNNPath)

    def exec(self):

        # change the date due to a Vivado bug
        # https://support.xilinx.com/s/question/0D52E00006uxy49SAA/vivado-fails-to-export-ips-with-the-error-message-bad-lexical-cast-source-type-value-could-not-be-interpreted-as-target?language=en_US

        try:
            subprocess.check_output("sudo timedatectl set-ntp false", shell=True)
            subprocess.check_output("sudo date -s '3 years ago'", shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Command failed with exit code {e.returncode}") from e


        config = hls4ml.utils.config_from_keras_model(self.model, granularity='name')
        hls_model = hls4ml.converters.convert_from_keras_model(
            self.model, 
            backend='VivadoAccelerator', 
            io_type='io_stream', 
            hls_config=config, 
            output_dir=f'{os.getcwd()}/{self.request.uuid}/{self.projectName}/'+'hls4ml_prj', 
            part=self.boardSpecs["part"])

        try:
            hls_model.compile()
        except Exception as e:
            raise Exception("Failed during compile of hls model "+str(e))

        try:
            hls_model.build(csim=False, synth=True, export=True, bitfile=True)
            with open(f'{os.getcwd()}/{self.request.uuid}/{self.projectName}/'+'hls4ml_prj/vivado.log', 'r') as logFile:
                for line in logFile:
                    if 'ERROR' in line:
                        raise Exception("Firmware generation has failed. Contact the admin.")
        except Exception as e:
            raise Exception("Failed during build of hls model "+str(e))

        # change again the date due to a Vivado bug
        # https://support.xilinx.com/s/question/0D52E00006uxy49SAA/vivado-fails-to-export-ips-with-the-error-message-bad-lexical-cast-source-type-value-could-not-be-interpreted-as-target?language=en_US
        
        try:
            subprocess.check_output("sudo timedatectl set-ntp true", shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Command failed with exit code {e.returncode}") from e

        
        