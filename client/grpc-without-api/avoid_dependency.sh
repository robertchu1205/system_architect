PROTOC_OUT=protos/
PROTOS=$(find . | grep "\.proto$")
for p in $PROTOS; do
  python -m grpc.tools.protoc -I . --python_out=$PROTOC_OUT --grpc_python_out=$PROTOC_OUT $p
done