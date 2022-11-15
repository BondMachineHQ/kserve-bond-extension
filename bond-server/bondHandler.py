import bond_pb2
import bond_pb2_grpc
import json
import grpc
from bondFirmwareHandler import BondFirmwareHandler

class BondHandler(bond_pb2_grpc.BondServerServicer):

    def load(self, request, context):
        try:
            bitfilename = request.bitfileName
            
            if bitfilename == None:
                return bond_pb2.LoadResponse(success=False, message="Bitfile is necessary")
            
            print("[DEBUG] Going to download bitstream from somewhere")
            
            print("[DEBUG] Loading firmware")
            #BondFirmwareHandler().load_bitsteam("proj_ebaz4205_neuralbond_expanded.bit")
            print("[DEBUG] Firmware loaded")
            
        except Exception as err:
            return bond_pb2.LoadResponse(success=False, message=str(err))
            
        return bond_pb2.LoadResponse(success=True, message="Bitstream loaded successfully")
    

    def predict(self, request, context):
        
        try:
            # {"inputs": [{"name": "input_1", "shape": [1, 28], "datatype": "FP32", "data": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]}]}
            inputs_received = json.loads(request.inputs)["inputs"] # array of inputs
            
            outputs = []
            
            for i in range(0, len(inputs_received)):
                input_name  = inputs_received[i]["name"] # input_1
                input_shape = inputs_received[i]["shape"] # [1,28]
                input_datatype = inputs_received[i]["datatype"] # "FP32",
                input_data = inputs_received[i]["data"] # [0.5, 0.5, ..]

                BondFirmwareHandler().predict(input_shape, input_data)
            
                reply = {}
                reply["name"] = input_name.replace("input_", "output_")
                reply["classification"] = {
                    "probabilities": [],
                    "classification": 1
                }
                outputs.append(reply)
                
            return bond_pb2.InputResponse(outputs=json.dumps(outputs))
                        
        except Exception as err:
            print("[DEBUG] Unable to make prediction")
            return grpc.ServicerContext().abort(500, str(err))
