# kserve-bond-extension

Project that extends KServe predictors, an emerging standard for ML (Machine Learning) model inference as a service on kubernetes. This project will support a custom workflow capable of loading and serving models on-demand on top of FPGAs. A key aspect is that the proposed approach makes the firmware generation transparent, often an obstacle to a widespread FPGA adoption.

# Load and build firmware

This is an example of input to send from the client:

```
{
  "bitfileName": "bm-axist-bankote"
}
```
The `bitfileName` is the the name of the bitstream file to download and load on FPGA. If the client sends only this information, it means that the bitstream file already exists and it is available to be used.
An example of reply to this message is:
```
{
  "success": true,
  "message": "Bitstream loaded successfully"
}
```
The message field warns the user of any errors that may occur in doing so.

This is another example of input to send from the client:

```
{
  "bitfileName": "bm-axist-bankote",
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
A streaming communication begins between the server requested by the original client and the server to build the firmware.
At the end of the procedure, the bitstream file will be uploaded in a public repository and it will be available to be used,



