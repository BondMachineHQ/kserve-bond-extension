import grpc

import buildfirmware_pb2
import buildfirmware_pb2_grpc

def run():
    print("called run")
    channel = grpc.insecure_channel('localhost:50051')
    print("channel created")
    stub = buildfirmware_pb2_grpc.BuildFirmwareServerStub(channel)
    print("before sending request")
    response_iterator = stub.buildFirmware(buildfirmware_pb2.BuildFirmwareRequest(
        uuid="27de1d71-1b98-4e22-aef9-5d85c05f3b35",
        projectName="test",
        hlsToolkit= "bondmachine",
        targetBoard= "zedboard",
        projectType= "neuralnetwork",
        nInputs= 4,
        nOutputs= 2,
        flavor= "axist",
        sourceNeuralNetwork= "banknote.json"
    ))
    print("going to iterate over response")
    for response in response_iterator:
        print("Success: ", response.success, " message: ", response.message)


if __name__ == '__main__':
    run()