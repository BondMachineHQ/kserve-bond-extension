import buildfirmware_pb2
import buildfirmware_pb2_grpc
import grpc
import os
from utils import PrintHandler
from bondProjectHandler import BondMachineProjectHandler
    
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
                    bmPrjHandler.exec(cmd)
                    yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message="command executed successfully: make "+cmd)
                
                yield buildfirmware_pb2.BuildFirmwareResponse(success=True, message="Bitstream process ended successfully")
            else:
                yield buildfirmware_pb2.BuildFirmwareResponse(success=False, message="hls toolkit not handled")
            
        except Exception as err:
            PrintHandler().print_fail(" * Loaded of bitstream file went wrong  "+str(err)+" *"+"\n")
            yield buildfirmware_pb2.BuildFirmwareResponse(success=False, message=str(err))
        