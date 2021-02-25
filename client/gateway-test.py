# For testing gateway
import os
import glob
# import time
import json
import base64
import requests
import argparse

def open_and_serialize_image(filename):
    with open(filename, "rb") as f:
        image = f.read()
    return base64.b64encode(image).decode("utf-8")

def createJson(path, IMAGE_AMOUNT):
    filenames = []
    for root, dirs, files in os.walk(path):
       for img_file in files:
            if img_file.endswith('.jpg'):
               filenames.append(os.path.join(root, img_file))
    instances = []
    for i,f in enumerate(filenames[:int(IMAGE_AMOUNT)]):
        instances.append({"image": {"b64":open_and_serialize_image(f)},"component": "ZZZ", "capacity": "270", "degree": "270", "voltage": "016", "sn": "CN0DRR0PWS30009E01E9A03"})
    payload = {"instances": instances}
    return payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="link & image amount")
    parser.add_argument("-l", "--link", dest="TFSERVER_URL", help="link of tfserving")
    parser.add_argument("-p", "--img_path", dest="IMAGE_PATH", help="Image Folder directory")
    parser.add_argument("-a", "--amount", dest="IMAGE_AMOUNT", help="image amount")
    args = parser.parse_args()
    IMAGE_PATH = args.IMAGE_PATH
    IMAGE_AMOUNT = args.IMAGE_AMOUNT
    TFSERVER_URL = args.TFSERVER_URL

    # print('IN POST')
    data = json.dumps(createJson(IMAGE_PATH,IMAGE_AMOUNT))
    header = {
        'content-type': "application/json"
    }
    response = requests.post(TFSERVER_URL, data=data, headers=header)
    print("response ok: {}".format(response.ok))
    print("outputs: {}".format(response.text))