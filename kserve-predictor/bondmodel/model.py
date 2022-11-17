import kserve
from typing import Dict
import bond_pb2
import bond_pb2_grpc
import grpc


class BondModel(kserve.Model):
    def __init__(self, name: str, bond_server_uri: str):
        super().__init__(name)
        self.name = name
        self.bond_server_uri = bond_server_uri
        self.load()

    def load(self):
        with grpc.insecure_channel(self.bond_server_uri) as channel:
            stub = bond_pb2_grpc.BondServerStub(channel)
            response = stub.SayHello(bond_pb2.LoadRequest(bitfileName='bondmachine_ml'))
            if response.success:
                print("Load client received: " + response.message)
            else:
                print("Load function failed")
        pass

    def predict(self, request: Dict) -> Dict:
        inputs = request["instances"]

        return {"predictions": inputs}


if __name__ == "__main__":
    model = BondModel("bond-model", "10.2.1.103:50051")
    model.load()
    kserve.ModelServer(workers=1).start([model])
