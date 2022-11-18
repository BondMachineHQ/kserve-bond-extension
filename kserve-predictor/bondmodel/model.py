import kserve
from typing import Dict
from .bond_pb2_grpc import BondServerStub
from .bond_pb2 import LoadRequest, InputRequest
import grpc
import json


class BondModel(kserve.Model):
    def __init__(self, name: str, bond_server_uri: str):
        super().__init__(name)
        self.name = name
        self.bond_server_uri = bond_server_uri
        self.loaded = False
        self.load()

    def load(self):
        if not self.loaded:
            print("loading firmware")
            try:
                with grpc.insecure_channel(self.bond_server_uri) as channel:
                    stub = BondServerStub(channel)
                    response = stub.load(LoadRequest(bitfileName='bondmachine_ml'))
                    if not response.success:
                        #https://github.com/kserve/kserve/blob/master/python/sklearnserver/sklearnserver/model.py#L40-L45
                        raise RuntimeError("Load function failed")
            except Exception as ex:
                raise RuntimeError("Load function failed:", ex)
            self.loaded = True
        pass

    def predict(self, request: Dict) -> Dict:
        # {'inputs':[{'name':'input_1','shape':[1,4],'datatype':'FP32','data':[0.39886742,0.76609776,-0.39003127,-0.58781728]}]}
        try:
            with grpc.insecure_channel(self.bond_server_uri) as channel:
                    stub = BondServerStub(channel)
                    response = stub.predict(InputRequest(inputs=json.dumps(request)))
        except Exception as ex:
            raise RuntimeError("Predict function failed:", ex)

        return dict(results=response.outputs)
