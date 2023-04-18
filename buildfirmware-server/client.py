import grpc

import buildfirmware_pb2
import buildfirmware_pb2_grpc
import uuid

import random
import string
import config

from minio import Minio
from minio.error import S3Error

import os

def generate_random_name(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def generateJob():
    return buildfirmware_pb2.BuildFirmwareRequest(
    uuid = str(uuid.uuid4()),
    projectName = generate_random_name(8),
    hlsToolkit = "bondmachine",
    targetBoard = "zedboard",
    projectType = "neuralnetwork",
    nInputs = 4,
    nOutputs = 2,
    flavor = "axist",
    sourceNeuralNetwork = "banknote.json")
    
def upload():
    client = Minio(
        "minio.131.154.96.26.myip.cloud.infn.it",
        access_key=config.username,
        secret_key=config.password,
    )
    
    client.fput_object(
        "fpga-firmware", "test.txt", os.getcwd()+"/test.txt",
    )
     
def run():
    channel = grpc.insecure_channel('10.2.129.49:50051')
    stub = buildfirmware_pb2_grpc.BuildFirmwareServerStub(channel)
    job = generateJob()
    response_iterator = stub.buildFirmware(job)
    for response in response_iterator:
        print("Success: ", response.success, " message: ", response.message)

if __name__ == '__main__':
    # upload()
    run()