import json
import requests
import time
import sys

#{"inputs":[{"name":"input_1","shape":[1,4],"datatype":"FP32","data":[0.39886742,0.76609776,-0.39003127,-0.58781728]}]}

model_name = sys.argv[1]

if len(sys.argv) < 3:
    dummy_input = json.loads("[0.39886742,0.76609776,-0.39003127,-0.58781728]") 
else:
    dummy_input = json.loads(sys.argv[2])

inference_request = {
  "inputs": []
}

#inputs_multiplied = [ dummy_input for _ in range(200) ]

#entry = {
#     "name" : "input_1",
#      "shape" : [ len(inputs_multiplied), len(inputs_multiplied[0]) ],
#      "datatype"  : "FP32",
#      "data" : inputs_multiplied
#}

entry = {
     "name" : "input_1",
      "shape" : [ 1, len(dummy_input) ],
      "datatype"  : "FP32",
      "data" : dummy_input
}

print(entry)
inference_request["inputs"].append(entry)

with open("test.json", "w") as f:
    json.dump(inference_request, f)

session = requests.Session()

import time

# base) ➜  kserve export SERVICE_HOSTNAME=testfpga.default.fpga.infn.it                                                                                     
# (base) ➜  kserve curl -vvv -H "Content-Type: application/json"  -H "Host: ${SERVICE_HOSTNAME}" -k http://10.2.202.18:31002/v1/models/bond-model:predict -d @fpga-input.json

start = time.time()
for _ in range(10):
    response = session.post(f"http://10.2.202.18:31002/v1/models/{model_name}:predict", json = inference_request, headers={"Host": f"{model_name}.default.fpga.infn.it"}) 
end = time.time()
print("Execution time: " + str((end - start)/10))

print("Status Code", response.status_code)
print("JSON Response ", response.json())