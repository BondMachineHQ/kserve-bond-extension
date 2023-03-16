import bond_pb2
import bond_pb2_grpc
import json
import grpc
from bondFirmwareHandlerMM import BondFirmwareHandlerMM
from hls4mlFirmwareHandler import Hls4mlFirmwareHandler
from downloadHandler import DownloadHandler
import os
from utils import PrintHandler
import subprocess
import numpy as np

class BondHandler(bond_pb2_grpc.BondServerServicer):

    def load(self, request, context):
        try:
            bitfilename = request.bitfileName
            
            if bitfilename == None:
                return bond_pb2.LoadResponse(success=False, message="Bitfile is necessary")
            
            PrintHandler().print_warning(" * Going to download bitstream * ")
            DownloadHandler().download_bitstream(bitfilename)
            DownloadHandler().check_bitstream(bitfilename)
            metadata_info = DownloadHandler().parse_metadata(bitfilename)
            PrintHandler().print_success(" * Finish download bitstream * ")
            
            PrintHandler().print_warning(" * Loading firmware * ")
            if metadata_info["predictor"] == "bondmachine":
                BondFirmwareHandlerMM().load_bitsteam(os.getcwd()+"/"+bitfilename+".bit", metadata_info["n_outputs"])
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
                
                for i in range(0, len(inputs_received)):
                    input_name  = inputs_received[i]["name"] # input_1
                    input_shape = inputs_received[i]["shape"] # [1,28]
                    input_datatype = inputs_received[i]["datatype"] # "FP32",
                    input_data = inputs_received[i]["data"] # [0.5, 0.5, ..]
                
                    reply["name"] = input_name.replace("input_", "output_")
                    
                    bm_prediction = BondFirmwareHandlerMM().predict(input_shape, input_data)
                    reply["classification"]["probabilities"] = bm_prediction[:2]
                    reply["classification"]["classification"] = bm_prediction[2]
                    
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
