import buildfirmware_pb2_grpc
import grpc
from concurrent import futures
import sys
from utils import PrintHandler
from buildFirmware import BuildFirmwareHandler
import subprocess
import os
from utils import PrintHandler

def checkDependencies(vivadoVersion):
    # check if bmhelper exists
    try:
        bmhelpercheck = subprocess.check_output("which bmhelper", shell=True)
    except:
        raise Exception("bm helper is not installed")

    # check if Vivado > 2019.2 is installed
    path = f'/opt/Xilinx/Vivado/{vivadoVersion}/bin'
    if not os.path.exists(path):
        raise Exception("Vivado path does not exists")

    os.environ['PATH'] = f'/opt/Xilinx/Vivado/{vivadoVersion}/bin:' + os.environ['PATH']

def serve():
    
    if len(sys.argv) < 3:
        PrintHandler().print_fail("[DEBUG] Port argument and vivado version are required")
        sys.exit(1)
    
    vivadoVersion = sys.argv[2]
    
    
    # try:
    #     checkDependencies(vivadoVersion)
    # except Exception as e:
    #     PrintHandler().print_fail("[DEBUG] An error occurred during check of dependencies: "+str(e))
    #     sys.exit(1)
    
    port = sys.argv[1]
    server = server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=100))
    buildfirmware_pb2_grpc.add_BuildFirmwareServerServicer_to_server(BuildFirmwareHandler(), server)
    server.add_insecure_port('[::]:'+port)
    PrintHandler().print_warning(" * "+"before starting server on port "+port+" *")
    server.start()
    PrintHandler().print_success(" * "+"after starting server on port "+port+" *")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()