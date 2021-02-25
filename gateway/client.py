# for gateway testing
import os
import json
import base64
import requests
import argparse
# 127.0.0.1 if it's the same container
# GATEWAY_URL = 'http://10.41.16.21:3333/predict'
# images in the assigned directory less than Batch size below would use all the images

parser = argparse.ArgumentParser(description='Link & image and amount')
parser.add_argument('-m', '--method', dest='METHOD',help='post OR get')
parser.add_argument('-g', '--gateway', dest='GATEWAY_URL', help='Link of gateway')
parser.add_argument('-p', '--img_path', dest='IMAGE_PATH', help='Walked img folder directory')
parser.add_argument('-a', '--amount', dest='IMAGE_AMOUNT', help='image amount')
parser.add_argument('-t', '--cap_type', dest='CAP_TYPE', help='CAP_TYPE')
parser.add_argument('-d', '--cap_degree', dest='CAP_DEGREE', help='CAP_DEGREE')
parser.add_argument('-s', '--split_one', dest='SPLIT_ONE', default='False', help='SPLIT_ONE, default:False')
parser.add_argument('--post_file', dest='POST_FILE', default='False', help='POST_FILE, default:False')
args = parser.parse_args()
IMAGE_PATH = args.IMAGE_PATH
IMAGE_AMOUNT = args.IMAGE_AMOUNT
GATEWAY_URL = args.GATEWAY_URL
METHOD = args.METHOD
CAP_TYPE = args.CAP_TYPE
CAP_DEGREE = args.CAP_DEGREE
SPLIT_ONE = args.SPLIT_ONE
POST_FILE = args.POST_FILE

def open_and_serialize_image(filepath):
    with open(filepath, 'rb') as f:
        image = f.read()
    return base64.b64encode(image).decode('utf-8')

def createJson(filepaths):
    instances = []
    for i, f in enumerate(filepaths):
        instances.append(
            {'image': {'b64':open_and_serialize_image(f)}, 
            'component':CAP_TYPE, 'degree':str(CAP_DEGREE), 'capacity':'NA', 
            'voltage':'NA', 'filename':f.split('/')[-1].split('.')[0]})
    payload = {'instances': instances}
    return payload

def mixed_createJson(filepaths):
    instances = []
    for i, f in enumerate(filepaths):
        if i is 1:
            instances.append(
                {'image': {'b64':open_and_serialize_image(f)}, 
                'component':'AluCap', 'degree':str(CAP_DEGREE), 'capacity':'820', 
                'voltage':'NA', 'filename':f.split('/')[-1].split('.')[0]})
        elif i is 2:
            instances.append(
                {'image': {'b64':open_and_serialize_image(f)}, 
                'component':'ElecCap', 'degree':str(CAP_DEGREE), 'capacity':'220', 
                'voltage':'NA', 'filename':f.split('/')[-1].split('.')[0]})
        elif i is 3:
            instances.append(
                {'image': {'b64':open_and_serialize_image(f)}, 
                'component':'BAD', 'degree':str(CAP_DEGREE), 'capacity':'820', 
                'voltage':'NA', 'filename':f.split('/')[-1].split('.')[0]})
        else:
            instances.append(
                {'image': {'b64':open_and_serialize_image(f)}, 
                'component':CAP_TYPE, 'degree':str(CAP_DEGREE), 'capacity':'NA', 
                'voltage':'NA', 'filename':f.split('/')[-1].split('.')[0]})
    payload = {'instances': instances}
    return payload

def to_amount_filepaths():
    filepaths = []
    for root, dirs, files in os.walk(IMAGE_PATH):
        for img_file in files:
            if img_file.endswith('.png'):
                filepaths.append(os.path.join(root, img_file))
            if img_file.endswith('.bmp'):
                filepaths.append(os.path.join(root, img_file))
            if img_file.endswith('.jpg'):
                filepaths.append(os.path.join(root, img_file))
    return filepaths[:int(IMAGE_AMOUNT)]

if __name__ == '__main__':
    if METHOD=='get':
        if GATEWAY_URL.split('//')[1][:3]=='127':
            savedir = '/tf/createJson.json' # local test
        else:
            savedir = '/tf/A1/data.json' # local test
        with open(savedir, 'w', encoding='utf-8') as f:
            json.dump(createJson(filepaths), 
                f, ensure_ascii=False, indent=4)
        response = requests.get(GATEWAY_URL)
        print('response ok: {}'.format(response.ok))
        print('outputs: {}'.format(response.text))
    elif METHOD=='post':
        filepaths = to_amount_filepaths()
        if POST_FILE=='False':
            # reading filepaths by os walk
            header = {
                        'content-type': 'application/json'
            }
            # send request every image
            if SPLIT_ONE != 'False':
                for f in filepaths:
                    data = json.dumps(createJson([f]))
                    response = requests.post(GATEWAY_URL, data=data, headers=header)
                    print('response ok: {}'.format(response.ok))
                    print('outputs: {}'.format(response.text))
            # send request by batch
            else:
                data = json.dumps(createJson(filepaths))
                response = requests.post(GATEWAY_URL, data=data, headers=header)
                print('response ok: {}'.format(response.ok))
                print('outputs: {}'.format(response.text))
                # outputs = response.json()['predictions']
        else:
            header = {
                        'Authorization': ''
            }
            # post with files={'img_file': open(img_path, 'rb')}
            if int(IMAGE_AMOUNT)==1 or (int(IMAGE_AMOUNT)>1 and SPLIT_ONE != 'False'):
                for fp in filepaths:
                    data = {
                        'img_name':f'SN_EAGLE_LOC_{CAP_TYPE}_{str(CAP_DEGREE)}_NA_NA_0.jpg',
                        'img_info':fp.split('/')[-1]
                    }
                    files = {
                        'img_file':open(fp, 'rb')
                    }
                    response = requests.post(GATEWAY_URL, data=data, headers=header, files=files)
                    print('response ok: {}'.format(response.ok))
                    print('outputs: {}'.format(response.text))
            # error while append
            else:
                instances = {
                            'img_name':[],
                            'img_info':[]
                    }
                img_file = []
                for i, f in enumerate(filepaths):
                    instances['img_name'].append(f'SN_EAGLE_LOC_{CAP_TYPE}_{str(CAP_DEGREE)}_270_NA_0.jpg')
                    instances['img_info'].append(f.split('/')[-1])
                    img_file.append(('img_file', open(f, 'rb')))
                # payload = {'instances': instances}
                # data = json.dumps(payload)
                response = requests.post(GATEWAY_URL, headers=header, data=instances, files=img_file)
                print('response ok: {}'.format(response.ok))
                print('outputs: {}'.format(response.text))
