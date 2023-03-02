import buildfirmware_pb2
import buildfirmware_pb2_grpc
import grpc
import os
from utils import PrintHandler
    
    
class BuildFirmwareHandler(buildfirmware_pb2_grpc.BuildFirmwareServerServicer):
    
    def buildFirmware(self, request, context):
        try:
            PrintHandler().print_success(" * Going to build firmware * ")
        except Exception as err:
            PrintHandler().print_fail(" * Loaded of bitstream file went wrong  "+str(err)+" *")
            return buildfirmware_pb2.BuildFirmwareResponse(success=False, message=str(err))
            
        return buildfirmware_pb2.BuildFirmwareResponse(success=True, message="Bitstream loaded successfully")