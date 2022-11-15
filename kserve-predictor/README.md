# kserve-bond-server

## Compile protobuf

Install dep

```bash
python -m pip install grpcio-tools
```

Compile the protobuf

```bash
python -m grpc_tools.protoc -I./protobuf --python_out=./bondmodel --pyi_out=./bondmodel --grpc_python_out=./bondmodel ./protobuf/bond.proto
```
