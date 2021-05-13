from concurrent import futures
import logging

import grpc
import json
import config

import ai_process_pb2
import ai_process_pb2_grpc
import google.protobuf.json_format

from resources.ai_process import main

class AIProcess(ai_process_pb2_grpc.AIProcessServicer):
    def PreProcess(self, request, context):
        error = False
        message = None

        body = google.protobuf.json_format.MessageToJson(request)
        body = json.loads(body)
        body['input'] = json.loads(body['input'])
        
        response = main(body, 'pre-process')
        data = json.dumps(response['result'])
        
        if not response['errorMessage'] == None:
            error = True
            message = response['errorMessage']

        return ai_process_pb2.ProcessReply(error=error, data=data, message=message)

    def PostProcess(self, request, context):
        error = False
        message = None

        body = google.protobuf.json_format.MessageToJson(request)
        body = json.loads(body)
        body['input'] = json.loads(body['input'])
        
        response = main(body, 'post-process')
        data = json.dumps(response['result'])
        
        if not response['errorMessage'] == None:
            error = True
            message = response['errorMessage']

        return ai_process_pb2.ProcessReply(error=error, data=data, message=message)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ai_process_pb2_grpc.add_AIProcessServicer_to_server(AIProcess(), server)
    server.add_insecure_port('[::]:' + config.GRPC_PORT)
    server.start()
    print('Serving by gRPC %s port'% config.GRPC_PORT)
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()