import bond_pb2_grpc
import grpc
from concurrent import futures
from bondHandler import BondHandler
import sys

def serve():
    
    if len(sys.argv) < 1:
        print("[DEBUG] Port argument is required")
        sys.exit(1)
        
    port = sys.argv[1]
    server = server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=100))
    bond_pb2_grpc.add_BondServerServicer_to_server(BondHandler(), server)
    server.add_insecure_port('[::]:'+port)
    print("[DEBUG] before starting server on port "+port)
    server.start()
    print("[DEBUG] after starting server on port "+port)
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
