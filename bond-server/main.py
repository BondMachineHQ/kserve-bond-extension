import bond_pb2_grpc
import grpc
from concurrent import futures
from bondHandler import BondHandler
import sys
from utils import PrintHandler

def serve():
    
    if len(sys.argv) < 1:
        print("[DEBUG] Port argument is required")
        sys.exit(1)
        
    port = sys.argv[1]
    server = server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=100))
    bond_pb2_grpc.add_BondServerServicer_to_server(BondHandler(), server)
    server.add_insecure_port('[::]:'+port)
    PrintHandler().print_warning(" * "+"starting GRPC server on port "+port+" *")
    server.start()
    PrintHandler().print_success(" * "+"running  GRPC server on port "+port+" *")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
