from bondmodel import BondModel
import kserve
import sys

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    model = BondModel(sys.argv[1], "10.2.1.118:50051")
    kserve.ModelServer(workers=1).start([model])
