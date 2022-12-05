import bond_pb2
import bond_pb2_grpc
import json
import grpc
from bondFirmwareHandler import BondFirmwareHandler
from downloadHandler import DownloadHandler
import os
from utils import PrintHandler
import subprocess

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
                BondFirmwareHandler().load_bitsteam(os.getcwd()+"/"+bitfilename+".bit", metadata_info["n_outputs"])
            PrintHandler().print_success(" * Firmware loaded * ")
            
        except Exception as err:
            PrintHandler().print_fail(" * Loaded of bitstream file went wrong  "+str(err)+" *")
            return bond_pb2.LoadResponse(success=False, message=str(err))
            
        return bond_pb2.LoadResponse(success=True, message="Bitstream loaded successfully")
    

    def predict(self, request, context):
        
        try:
            PrintHandler().print_warning(" * Request to make prediction * ")
            # {"inputs": [{"name": "input_1", "shape": [1, 28], "datatype": "FP32", "data": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]}]}
            
            input_parsed = request.inputs.replace("\'", "\"")
            inputs_received = json.loads(input_parsed)["inputs"] # array of inputs
            
            outputs = []
            
            for i in range(0, len(inputs_received)):
                input_name  = inputs_received[i]["name"] # input_1
                input_shape = inputs_received[i]["shape"] # [1,28]
                input_datatype = inputs_received[i]["datatype"] # "FP32",
                input_data = inputs_received[i]["data"] # [0.5, 0.5, ..]
            
                reply = {}
                reply["name"] = input_name.replace("input_", "output_")
                reply["classification"] = {
                    "probabilities": [],
                    "classification": 1
                }
                
                bm_prediction = BondFirmwareHandler().predict(input_shape, input_data, 2)
                reply["classification"]["probabilities"] = bm_prediction[:2]
                reply["classification"]["classification"] = bm_prediction[2]
                
                outputs.append(reply)
                
                PrintHandler().print_success(" * Prediction done successfully * ")
                
            return bond_pb2.InputResponse(success=True, outputs=json.dumps(outputs).replace("\'", "\""))
                        
        except Exception as err:
            PrintHandler().print_fail(" * Prediction went wrong  "+str(err)+" *")
            return bond_pb2.LoadResponse(success=False, message="Unable to make prediction"+str(err))
