### Generate Warmup requests. ###
import tensorflow as tf
import requests, base64, argparse, os

from tensorflow.python.framework import tensor_util
from tensorflow_serving.apis import classification_pb2
from tensorflow_serving.apis import inference_pb2
from tensorflow_serving.apis import model_pb2
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_log_pb2
from tensorflow_serving.apis import regression_pb2

parser = argparse.ArgumentParser(description="args")
parser.add_argument("-i", "--img_path", dest="img_path", help="img_path for encoding to base64")
parser.add_argument("-m", "--model_origin", dest="model_origin", help="to know what kinds of input/output specs gonna be")
parser.add_argument("-n", "--model_name", dest="MODEL_NAME", help="MODEL_NAME")
parser.add_argument("-s", "--signature", default="classification", dest="SIG", help="Default classification")
parser.add_argument("--inputs", default="string_array", dest="INPUTS", help="Default string_array")
parser.add_argument("--target", default="/p3/", dest="target_path", help="Default /p3/")

args = parser.parse_args()
img_path = args.img_path
model_origin = args.model_origin
SIG = args.SIG
MODEL_NAME = args.MODEL_NAME
INPUTS = args.INPUTS
target_path = args.target_path

def saiap_open_image(filename):
    image = open(filename, "rb").read()
    image = base64.urlsafe_b64encode(image)
    return image

def open_image(filename):
    with open(filename, "rb") as f:
        image = f.read()
    return image

def main():
    ### Generate TFRecords for warming up. ###
    global filename
    for root, dirs, files in os.walk(img_path):
        for img_file in files:
            if img_file.endswith(".png") or img_file.endswith(".bmp") or img_file.endswith(".jpg"):
                filename = os.path.join(root, img_file)
                break
    print(filename)
    with tf.io.TFRecordWriter(f"{target_path}tf_serving_warmup_requests") as writer:
        # replace <request> with one of:
        # predict_pb2.PredictRequest(..)
        # classification_pb2.ClassificationRequest(..)
        # regression_pb2.RegressionRequest(..)
        # inference_pb2.MultiInferenceRequest(..)
        
        ### Method 1 ###
        if model_origin == "saiap":
            request = predict_pb2.PredictRequest()
            request.model_spec.name = MODEL_NAME
            request.model_spec.signature_name = SIG
            request.inputs[INPUTS].CopyFrom(
                tensor_util.make_tensor_proto([saiap_open_image(filename)], tf.string)
            )
        elif model_origin == "wzsda":
            ## Method 2 ###
            request = predict_pb2.PredictRequest(
                model_spec=model_pb2.ModelSpec(name=MODEL_NAME, signature_name=SIG),
                inputs={
                    INPUTS: tensor_util.make_tensor_proto([open_image(filename)], tf.string),
                    "degree": tensor_util.make_tensor_proto(["0"], tf.string)
                }
            )
        else:
            print(f"arg 'model_origin' {model_origin} is not supported!")
        log = prediction_log_pb2.PredictionLog(
            predict_log=prediction_log_pb2.PredictLog(request=request))
        writer.write(log.SerializeToString())

if __name__ == "__main__":
    main()