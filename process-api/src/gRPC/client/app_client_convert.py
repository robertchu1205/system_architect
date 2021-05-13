import json 
import grpc 
import ai_process_pb2 
import ai_process_pb2_grpc 
def run(): 
    mode_res = [{ 
        'model_name': 'NNs_R_0402', 
        'model_output': ( 
            [1.6522163e-06, 0.999992, 3.9777913e-07, 3.4067274e-10, 2.0983299e-08, 5.9437e-06, 3.4067274e-10, 2.0983299e-08] 
        ), 
        'model_label': ( 
            ['MISS', 'OK', 'OK', 'POOR', 'SHIFT', 'UNCONFIRMED', 'POOR', 'SHIFT'] 
        ) 
    }, 
    ] 
    # integrage 
    input = { 
        "roi_name": 'NNs_R_0402', 
        'model_name': 'NNs_R_0402', 
        "model_result": json.dumps(mode_res) 
    } 
     
    input = json.dumps(input) 
    processes = [  
        "convert",
        "integrate"
    ]
    with grpc.insecure_channel('192.168.16.185:50051') as channel:  
    # with grpc.insecure_channel('localhost:50051') as channel: 
        stub = ai_process_pb2_grpc.AIProcessStub(channel) 
        response = stub.PostProcess(ai_process_pb2.ProcessRequest(input=input, processes=processes)) 
     
    result = { 
        "error": response.error, 
        "data": json.loads(response.data), 
        "message": response.message 
    } 
    print(result) 
if __name__ == '__main__': 
    run()