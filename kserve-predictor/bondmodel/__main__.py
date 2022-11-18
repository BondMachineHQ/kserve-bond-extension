from bondmodel import BondModel
import kserve

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    model = BondModel("bond-model", "10.2.1.103:50051")
    kserve.ModelServer(workers=1).start([model])