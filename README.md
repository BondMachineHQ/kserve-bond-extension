# kserve-bond-extension

Project that extends KServe predictors, an emerging standard for ML (Machine Learning) model inference as a service on kubernetes. This project will support a custom workflow capable of loading and serving models on-demand on top of FPGAs. A key aspect is that the proposed approach makes the firmware generation transparent, often an obstacle to a widespread FPGA adoption.

## Bond-server - Load

The **bond-server** is the grpc-server that has been designed to work on hybrid architectures (ARM + FPGA). For example, the ZYNQ programmable SoC family integrates the software programmability of an ARM based processor with the hardware programmability of the FPGA.
In our scenario, the board used is the *zedboard*. 

### Load and build firmware

This is an example of input to send from the client:

```
{
  "bitfileName": "bm-axist-bankote"
}
```
The `bitfileName` is the the name of the bitstream file to download and load on FPGA. If the client sends only this information, it means that the bitstream file already exists and it is available to be used. In our case, the bitstream file and it's associated metadata, are available on a MinIO bucket where all the bistream are stored.
The metadata associated with the bitstream are necessary to configure the board in order to be able to perform inference.
For example, those are the information related to a firmware:
```
{
    "board": "zedboard",
    "n_inputs": 4,
    "n_outputs": 2,
    "predictor": "bondmachine",
    "dataset": "banknote-authentication",
    "flavor": "axist",
    "benchcore": true
}
```
- **board** the target board for which the firmware is associated
- **n_inputs** the number of inputs (i.e features) that the ML model synthesized in hardware expects
- **n_outputs** the number of outputs that the ML model synthesized in hardware returns
- **predictor** the HLS toolkit used to build the firmware 
- **dataset** the dataset used to train the ML model
- **flavor** (only for BondMachine predictor) the flavor indicates the AXI protocol to use
- **benchcore** (only for BondMachine predictor) the benchcore flag indicates if the bondmachine architecture generated has an additional output which returns the number of clock cycles used for a prediction.

An example of reply to this message is:
```
{
  "success": true,
  "message": "Bitstream loaded successfully"
}
```
The message field warns the user of any errors that may occur doing this operation.

This is another example of input to send from the client:

```
{
  "bitfileName": "bm-axist-bankote",
  "buildfirmware": true,
  "hlsToolkit": "bondmachine",
  "targetBoard": "zedboard",
  "projectType": "neuralnetwork",
  "nInputs": 4,
  "nOutputs": 2,
  "flavor": "axist",
  "sourceNeuralNetwork": "banknote.json"
}
```
In this case, when those information are sent, it means that the client asks to build the firmware. The `bitfileName` is not used anymore to download and load, but the other information are used to build the firmware using another grpc-server that is running on a dedicated host that has all the requirements and tools in order to build the firmware requested. 
A streaming communication begins between the server running on the ZYNQ board and the server to build the firmware.

## Buildfirmware-server

This is the GRPC-server that is running on a dedicated host that has all the requirements to build a firmware starting from the requirements asked by the client in the previous steps.
This dedicated host is configured with all the packages necessary to build the firmware:
- Vivado
- `The BondMachine toolkit`

BondMachine (http://bondmachine.fisica.unipg.it/) is an High Level Synthesis framework with a lot of features: thanks to this framework, it is possible to build a firmware which makes inference in a simple and user-friendly way.
The BondMachine toolkit has an helper tool called **bmhelper** that allows to build a project with all the configurations sent from the client.
The firmware generation is transparent to the user. At the end of the procedure, the bitstream file will be uploaded in a MinIO bucket and it will be available to be used.

---

## Bond-server - Inference

After the load of the bitstream, the FPGA is configured to be used for machine learning inference.
This is an example of input to send in order to make the inference:
```
{
  "inputs": "{'inputs':[{'name':'input_1','shape':[2,4],'datatype':'FP32','data':[[ 0.39886742,0.76609776,-0.39003127,-0.58781728],[-0.24941276,1.07705921,-1.07095774,-0.64423373]]}]}"
}
```
The client sends an array of inputs which must be consistent with the previously loaded firmware. In this example, the number of features was 4 and a sample has shape (n, 4).
this is the corresponding answer:
```
{
  "success": true,
  "outputs": "[{"classification": {"probabilities": [[0.6876530051231384, 0.3123469352722168], [0.5749054551124573, 0.42509448528289795]], "classification": [0.0, 0.0]}}]"
}
```
The client is returned the probabilities of the samples for which it has requested analysis.