import os, json, base64
import requests, argparse, time
# 127.0.0.1 if it's the same container
### python gateway
# GATEWAY_URL = 'http://10.41.16.21:3333/predict'
### go gateway
# GATEWAY_URL = 'http://10.41.242.29:30501/v1/models/model:predict'
# images in the assigned directory less than Batch size below would use all the images
ini_sec = time.time()

parser = argparse.ArgumentParser(description='Request Information')
parser.add_argument('-m', '--method', dest='METHOD',help='post OR get')
parser.add_argument('-g', '--gateway', dest='GATEWAY_URL', help='API of gateway')
parser.add_argument('-p', '--img_path', dest='IMAGE_PATH', help='folder directory to os.walk images below')
parser.add_argument('-a', '--amount', dest='IMAGE_AMOUNT', help='image amount')
parser.add_argument('-t', '--cap_type', dest='CAP_TYPE', help='CAP_TYPE')
parser.add_argument('-d', '--cap_degree', dest='CAP_DEGREE', help='CAP_DEGREE')
parser.add_argument('-s', '--split_one', dest='SPLIT_ONE', default='False', help='if request with a batch of images splitted to one in every request')
parser.add_argument('--post_file', dest='POST_FILE', default='False', help='False: image decoded to base64 string (DIP); True: image as binary string in request.file (ONEAI SMT - AIClient)')
args = parser.parse_args()

def open_and_serialize_image(filepath):
    with open(filepath, 'rb') as f:
        image = f.read()
    return base64.b64encode(image).decode('utf-8')

def createJson(filepaths):
    instances = []
    for i, f in enumerate(filepaths):
        ### depends on projects' definations
        instances.append(
        {   
            'image': {'b64':open_and_serialize_image(f)}, 
            'SN':'XXX',
            'component':args.CAP_TYPE, 
            'degree':str(args.CAP_DEGREE), 
            'capacity':'470', 
            'voltage':'6.3', 
            # 'filename':'20210426143811_XXX_OP3080_NA_NA_NA',
            # 'ErrorCode': '',
        })
    payload = {'instances': instances}
    return payload

def mixed_createJson(filepaths):
    instances = []
    for i, f in enumerate(filepaths):
        if i is 1:
            instances.append(
                {'image': {'b64':open_and_serialize_image(f)}, 
                'component':'AluCap', 'degree':str(args.CAP_DEGREE), 'capacity':'820', 
                'voltage':'NA', 'filename':f.split('/')[-1].split('.')[0]})
        elif i is 2:
            instances.append(
                {'image': {'b64':open_and_serialize_image(f)}, 
                'component':'ElecCap', 'degree':str(args.CAP_DEGREE), 'capacity':'220', 
                'voltage':'NA', 'filename':f.split('/')[-1].split('.')[0]})
        elif i is 3:
            instances.append(
                {'image': {'b64':open_and_serialize_image(f)}, 
                'component':'BAD', 'degree':str(args.CAP_DEGREE), 'capacity':'820', 
                'voltage':'NA', 'filename':f.split('/')[-1].split('.')[0]})
        else:
            instances.append(
                {'image': {'b64':open_and_serialize_image(f)}, 
                'component':args.CAP_TYPE, 'degree':str(args.CAP_DEGREE), 'capacity':'NA', 
                'voltage':'NA', 'filename':f.split('/')[-1].split('.')[0]})
    payload = {'instances': instances}
    return payload

def to_amount_filepaths():
    filepaths = []
    for root, dirs, files in os.walk(args.IMAGE_PATH):
        for img_file in files:
            if img_file.endswith('.png'):
                filepaths.append(os.path.join(root, img_file))
            if img_file.endswith('.bmp'):
                filepaths.append(os.path.join(root, img_file))
            if img_file.endswith('.jpg'):
                filepaths.append(os.path.join(root, img_file))
    return filepaths[:int(args.IMAGE_AMOUNT)]

if __name__ == '__main__':
    if args.METHOD=='get':
        if args.GATEWAY_URL.split('//')[1][:3]=='127':
            savedir = '/tf/createJson.json' # local test
        else:
            savedir = '/tf/A1/data.json' # local test
        with open(savedir, 'w', encoding='utf-8') as f:
            json.dump(createJson(filepaths), 
                f, ensure_ascii=False, indent=4)
        response = requests.get(args.GATEWAY_URL)
        print('response ok: {}'.format(response.ok))
        print('outputs: {}'.format(response.text))
        # print(f'dict: {response.__dict__}')
    elif args.METHOD=='post':
        filepaths = to_amount_filepaths()
        if args.POST_FILE=='False':
            # reading filepaths by os walk
            header = {
                        'content-type': 'application/json'
            }
            # send request every image
            if args.SPLIT_ONE != 'False':
                for f in filepaths:
                    data = json.dumps(createJson([f]))
                    response = requests.post(args.GATEWAY_URL, data=data, headers=header)
                    print('response ok: {}'.format(response.ok))
                    print('outputs: {}'.format(response.text))
                    # print(f'dict: {response.__dict__}')
            # send request by batch
            else:
                data = json.dumps(createJson(filepaths))
                response = requests.post(args.GATEWAY_URL, data=data, headers=header)
                print('response ok: {}'.format(response.ok))
                print('outputs: {}'.format(response.text))
                # print(f'dict: {response.__dict__}')
                # outputs = response.json()['predictions']
        else:
            header = {
                        'Authorization': ''
            }
            # post with files={'img_file': open(img_path, 'rb')}
            if int(args.IMAGE_AMOUNT)==1 or (int(args.IMAGE_AMOUNT)>1 and args.SPLIT_ONE != 'False'):
                for fp in filepaths:
                    data = {
                        'img_name':fp.split('/')[-1],
                        'img_info':'img_info',
                        'protocol':'grpc',
                    }
                    files = {
                        'img_file':open(fp, 'rb')
                    }
                    response = requests.post(args.GATEWAY_URL, data=data, headers=header, files=files)
                    print('response ok: {}'.format(response.ok))
                    print('outputs: {}'.format(response.text))
                    # print(f'dict: {response.__dict__}')
            # error while append
            else:
                instances = {
                            'img_name':[],
                            'img_info':[]
                    }
                img_file = []
                for i, f in enumerate(filepaths):
                    instances['img_name'].append(f.split('/')[-1])
                    instances['img_info'].append(i)
                    img_file.append(('img_file', open(f, 'rb')))
                # payload = {'instances': instances}
                # data = json.dumps(payload)
                response = requests.post(args.GATEWAY_URL, headers=header, data=instances, files=img_file)
                print('response ok: {}'.format(response.ok))
                print('outputs: {}'.format(response.text))
                # print(f'dict: {response.__dict__}')
    sec_taken = time.time() - ini_sec
    # print(data)
    print(f'client request to receive:{sec_taken} secs')