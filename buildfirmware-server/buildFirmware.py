import buildfirmware_pb2
import buildfirmware_pb2_grpc
import grpc
import os
from utils import PrintHandler
from bondProjectHandler import BondMachineProjectHandler
from hls4mlFirmwareHandler import HLS4MLProjectHandler
from minio import Minio
from minio.error import S3Error
import json
from subprocess import run
import config 

class BuildFirmwareHandler(buildfirmware_pb2_grpc.BuildFirmwareServerServicer):
    
    def buildFirmware(self, request, context):
        try:
            PrintHandler().print_warning(" * Request arrived to build firmware * ")
            
            yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message="Request accepted")
            
            hlsToolkit = request.hlsToolkit
            if hlsToolkit == None:
                raise Exception("hlsToolkit is required")
            
            PrintHandler().print_warning(" * Raw data arrived * "+str(request))

            if hlsToolkit == "bondmachine":
                
                bmPrjHandler = BondMachineProjectHandler(request)
                bmPrjHandler.checkRequirements()
                commands = bmPrjHandler.build()

                for cmd in commands:
                    yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message="Before exec command: make "+cmd)
                    bmPrjHandler.exec(cmd)
                    yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message="command executed successfully: make "+cmd)

                json_bitstream_info = {
                    "board": request.targetBoard,
                    "arch": request.arch,
                    "n_inputs": request.nInputs,
                    "n_outputs": request.nOutputs,
                    "predictor": hlsToolkit,
                    "flavor": request.flavor,
                    "benchcore": False
                }

            elif hlsToolkit == "hls4ml":

                hls4mlPrjHandler = HLS4MLProjectHandler(request)
                hls4mlPrjHandler.checkRequirements()
                yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message="check requirements completely successfully")
                hls4mlPrjHandler.exec()
                yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message="build of firmware completely successfully")
                json_bitstream_info = { "board": request.targetBoard,"arch": request.arch,"predictor": hlsToolkit }
            
            else:
                yield buildfirmware_pb2.BuildFirmwareResponse(success=False, message="hls toolkit not handled")

            bitstream_filename = request.uuid+"firmware.bit"
            hwh_filename = request.uuid+"firmware.hwh"

            with open(request.uuid+"firmware.json", 'w') as fp:
                json.dump(json_bitstream_info, fp)
            
            client = Minio(
                "minio.131.154.96.26.myip.cloud.infn.it",
                access_key=config.username,
                secret_key=config.password,
            )
            
            bitfile_path_cmd = run("cd "+request.uuid+" && find . -name *.bit", capture_output=True, shell=True).stdout.decode("utf8")[2:]
            hwh_path_cmd = run("cd "+request.uuid+" && find . -name *.hwh", capture_output=True, shell=True).stdout.decode("utf8")[2:]
            
            bitfile_path = request.uuid+"/"+bitfile_path_cmd
            hwh_path = request.uuid+"/"+hwh_path_cmd
            
            client.fput_object("fpga-models", request.uuid+"_firmware.bit", os.getcwd()+"/"+bitfile_path.replace("\n", ""))
            client.fput_object("fpga-models", request.uuid+"_firmware.hwh", os.getcwd()+"/"+hwh_path.replace("\n", ""))
            client.fput_object("fpga-models", request.uuid+"_firmware.json", os.getcwd()+"/"+request.uuid+"firmware.json")
            
            run("rm -rf "+os.getcwd()+"/"+request.uuid, capture_output=False, shell=True)
            run("rm -rf "+os.getcwd()+"/"+request.uuid+"firmware.json", capture_output=False, shell=True)

            yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message=request.uuid+"_firmware")
            
        except Exception as err:
            PrintHandler().print_fail(" * Loaded of bitstream file went wrong  "+str(err)+" *"+"\n")
            yield buildfirmware_pb2.BuildFirmwareResponse(success=False, message=str(err))
        