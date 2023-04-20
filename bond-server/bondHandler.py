import bond_pb2
import bond_pb2_grpc
import json
import grpc
from bondFirmwareHandlerMM import BondFirmwareHandlerMM
from bondFirmwareHandlerST import BondFirmwareHandlerST
from hls4mlFirmwareHandler import Hls4mlFirmwareHandler
from buildFirmwareHandler import BuildFirmwareHandler
from downloadHandler import DownloadHandler
import os
from utils import PrintHandler
import subprocess
import numpy as np

class BondHandler(bond_pb2_grpc.BondServerServicer):

    def load(self, request, context):
        try:
            PrintHandler().print_warning(" * Request for download arrived * ")
            
            bitfilename = request.bitfileName.replace(" ", "")
            hlsToolkit = request.hlsToolkit.replace(" ", "")
            
            if bitfilename == None:
                return bond_pb2.LoadResponse(success=False, message="Bitfile is necessary")
            
            if request.buildfirmware == True:
                PrintHandler().print_warning(" *  Creation of bitstream requested with toolkit "+hlsToolkit+" * ")
                
                targetBoard = request.targetBoard.replace(" ", "")
                projectType = request.projectType.replace(" ", "")
                nInputs = request.nInputs
                nOutputs = request.nOutputs
                flavor = request.flavor.replace(" ", "")
                sourceNeuralNetwork = request.sourceNeuralNetwork.replace(" ", "")
                
                if len(targetBoard) == 0 or len(projectType) == 0 or len(flavor) == 0 or len(sourceNeuralNetwork) == 0:
                    return bond_pb2.LoadResponse(success=False, message="You ask to build the firmware, but some information is missing. Check the doc")
                
                PrintHandler().print_warning(" *  Going to generate job to build firmware * ")
                bitfilename = BuildFirmwareHandler().generateJob(
                    hlsToolkit=hlsToolkit, 
                    projectType=projectType, 
                    flavor=flavor, 
                    nInputs=nInputs,
                    nOutputs=nOutputs, 
                    sourceNeuralNetwork=sourceNeuralNetwork,
                    targetBoard=targetBoard)
            
            PrintHandler().print_warning(" * Going to download bitstream * ")
            DownloadHandler().download_bitstream(bitfilename)
            DownloadHandler().check_bitstream(bitfilename)
            metadata_info = DownloadHandler().parse_metadata(bitfilename)
            PrintHandler().print_success(" * Finish download bitstream * ")
            
            PrintHandler().print_warning(" * Loading firmware * ")
            if metadata_info["predictor"] == "bondmachine":
                DownloadHandler().set_flavor(metadata_info["flavor"])
                if metadata_info["flavor"] == "aximm":
                    BondFirmwareHandlerMM().load_bitsteam(os.getcwd()+"/"+bitfilename+".bit", metadata_info["n_outputs"])
                elif metadata_info["flavor"] == "axist":
                    if metadata_info["benchcore"] == True:
                        n_outputs = metadata_info["n_outputs"] + 1
                    else:
                        n_outputs = metadata_info["n_outputs"]
                    BondFirmwareHandlerST().load_bitsteam(os.getcwd()+"/"+bitfilename+".bit", metadata_info["n_inputs"], n_outputs, metadata_info["benchcore"])
            elif  metadata_info["predictor"] == "hls4ml":
                Hls4mlFirmwareHandler().load_bitsteam(os.getcwd()+"/"+bitfilename+".bit", (64, metadata_info["n_inputs"]), (64, metadata_info["n_outputs"]))  
            else:
                raise Exception("predictor not handled")
            
            DownloadHandler().set_predictor(metadata_info["predictor"])
            
            PrintHandler().print_success(" * Firmware loaded * ")
            
        except Exception as err:
            PrintHandler().print_fail(" * Loaded of bitstream file went wrong  "+str(err)+" *")
            return bond_pb2.LoadResponse(success=False, message=str(err))
            
        return bond_pb2.LoadResponse(success=True, message="Bitstream loaded successfully")
    

    def predict(self, request, context):
        
        try:
            predictor = DownloadHandler().get_predictor()
            
            PrintHandler().print_warning(" * Request to make prediction with  "+predictor+" *")
            # {"inputs": [{"name": "input_1", "shape": [1, 28], "datatype": "FP32", "data": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]}]}
            
            input_parsed = request.inputs.replace("\'", "\"")
            inputs_received = json.loads(input_parsed)["inputs"] # array of inputs
            
            outputs = []
            
            reply = {}
            reply["classification"] = {
                "probabilities": [],
                "classification": 1
            }
                    
            if predictor == "bondmachine":
                
                flavor = DownloadHandler().get_flavor()
                
                for i in range(0, len(inputs_received)):
                    if flavor == "aximm":
                        input_name  = inputs_received[i]["name"] # input_1
                        input_shape = inputs_received[i]["shape"] # [1,28]
                        input_datatype = inputs_received[i]["datatype"] # "FP32",
                        input_data = inputs_received[i]["data"] # [0.5, 0.5, ..]
                    
                        reply["name"] = input_name.replace("input_", "output_")
                        
                        bm_prediction = BondFirmwareHandlerMM().predict(input_shape, input_data)
                        reply["classification"]["probabilities"] = bm_prediction[:2]
                        reply["classification"]["classification"] = bm_prediction[2]
                        
                        outputs.append(reply)
                        
                    elif flavor == "axist":
                        input_data = inputs_received[i]["data"] # [[0.5, 0.5, ..]]
                        y_predicts = BondFirmwareHandlerST().predict(input_data)
                        
                        probabilites = []
                        classifications = []
                        for pred in y_predicts:
                            probabilites.append(pred[:2])
                            classifications.append(pred[2])
                            
                        reply["classification"]["probabilities"] = probabilites
                        reply["classification"]["classification"] = classifications
                        
                        outputs.append(reply)
                    
            elif predictor == "hls4ml":
                 
                for i in range(0, len(inputs_received)):
                    
                    input_shape = inputs_received[i]["shape"] # [1,28]
                    input_data = np.asarray([inputs_received[i]["data"]]) # [0.5, 0.5, ..]
                    input_name  = inputs_received[i]["name"] # input_1
                    
                    reply["name"] = input_name.replace("input_", "output_")
                    
                    y_predicts = Hls4mlFirmwareHandler().predict(input_data)
                    
                    reply["classification"]["probabilities"] = y_predicts[:2]
                    reply["classification"]["classification"] = y_predicts[2]
                    
                    outputs.append(reply)
                
            PrintHandler().print_success(" * Prediction done successfully with predictor "+predictor+" * ")
                
            return bond_pb2.InputResponse(success=True, outputs=json.dumps(outputs).replace("\'", "\""))
                        
        except Exception as err:
            PrintHandler().print_fail(" * Prediction went wrong  "+str(err)+" *")
            return bond_pb2.LoadResponse(success=False, message="Unable to make prediction"+str(err))
