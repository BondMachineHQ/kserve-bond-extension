import buildfirmware_pb2
import buildfirmware_pb2_grpc
import grpc
import os
from utils import PrintHandler
from bondProjectHandler import BondMachineProjectHandler
from minio import Minio
from minio.error import S3Error
import json
from subprocess import run

class BuildFirmwareHandler(buildfirmware_pb2_grpc.BuildFirmwareServerServicer):
    
    def buildFirmware(self, request, context):
        try:
            PrintHandler().print_success(" * Going to build firmware * ")
            
            yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message="Request accepted")
            
            hlsToolkit = request.hlsToolkit
            if hlsToolkit == None:
                raise Exception("hlsToolkit is required")
            
            if hlsToolkit == "bondmachine": 
                bmPrjHandler = BondMachineProjectHandler(request)
                bmPrjHandler.checkRequirements()
                commands = bmPrjHandler.build()
                for cmd in commands:
                    yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message="Before exec command: make "+cmd)
                    bmPrjHandler.exec(cmd)
                    yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message="command executed successfully: make "+cmd)
                
                bitstream_filename = request.uuid+"firmware.bit"
                hwh_filename = request.uuid+"firmware.hwh"
                
                json_bitstream_info = {
                    "board": request.targetBoard,
                    "n_inputs": request.nInputs,
                    "n_outputs": request.nOutputs,
                    "predictor": hlsToolkit,
                    "flavor": request.flavor,
                    "benchcore": False
                }

                with open(request.uuid+"firmware.json", 'w') as fp:
                    json.dump(json_bitstream_info, fp)
                
                client = Minio(
                    "minio.131.154.96.26.myip.cloud.infn.it",
                    access_key=config.username,
                    secret_key=config.password,
                )
                
                bitfile_path_cmd = run("find . -name *.bit", capture_output=True, shell=True).stdout.decode("utf8")[2:]
                hwh_path_cmd = run("find . -name *.bit", capture_output=True, shell=True).stdout.decode("utf8")[2:]
                
                bitfile_path = bitfile_path_cmd[:bitfile_path_cmd.rindex(".bit")]+".bit"
                hwh_path = hwh_path_cmd[:hwh_path_cmd.rindex(".hwh")]+".hwh"
                
                client.fput_object(
                    "fpga-firmware", request.uuid+"firmware.bit", os.getcwd()+"/"+bitfile_path,
                )
                client.fput_object(
                    "fpga-firmware", request.uuid+"firmware.hwh", os.getcwd()+"/"+hwh_path,
                )
                client.fput_object(
                    "fpga-firmware", request.uuid+"firmware.json", os.getcwd()+"/"+request.uuid+"firmware.json",
                )
                
                yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message="Bitstream process ended successfully")
            else:
                yield buildfirmware_pb2.BuildFirmwareResponse(success=False, message="hls toolkit not handled")
            
        except Exception as err:
            PrintHandler().print_fail(" * Loaded of bitstream file went wrong  "+str(err)+" *"+"\n")
            yield buildfirmware_pb2.BuildFirmwareResponse(success=False, message=str(err))
        