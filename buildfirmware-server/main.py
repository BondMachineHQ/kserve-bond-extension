import buildfirmware_pb2_grpc
import grpc
from concurrent import futures
import sys
from utils import PrintHandler
from buildFirmware import BuildFirmwareHandler

def serve():
    
    if len(sys.argv) < 1:
        print("[DEBUG] Port argument is required")
        sys.exit(1)
        
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
