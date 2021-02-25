import os

def parse_image_filename(filename):
    try:
        symbols = {}
        possible_bool = False
        symbols.update({'filename': filename}) # 20201224000000_CN0RM5DRWS20007600PAA00_Screw1_270_220_NA.jpg
        filename = os.path.splitext(filename)[0]
        possible_comps = ['Screw', 'DIMM']
        symbols.update({'timestamp': filename.split('_')[0]}) # 20201224000000
        symbols.update({'SN': filename.split('_')[1]}) # CN0RM5DRWS20007600PAA00
        symbols.update({'location': filename.split('_')[2]}) # Screw1
        symbols.update({'degree': filename.split('_')[3]}) # 270
        symbols.update({'capacity': filename.split('_')[4]}) # 220
        symbols.update({'voltage': filename.split('_')[5]}) # NA
        for pc in possible_comps:
            if pc in symbols['location']:
                possible_bool = True
                symbols.update({'component': pc}) # Screw
        if possible_bool == False:
            symbols.update({'component': symbols['location']})
    except Exception as e:
        return e
    return symbols

def file_in_body_request(request):
    try:
        if (not request) or ('instances' not in request):
            return (False, 'instances not in request.json')
        data = request
        for idx, d in enumerate(data['instances']):
            symbols = parse_image_filename(d['filename'])
            if symbols == {}:
                return (False, 'possible_comps does not exist in filename')
            elif type(symbols) == str:
                return (False, symbols)
            for key, value in symbols.items():
                d.update({key: value})
    except Exception as e:
        return (False, e)
    return (True, data)

class handler:
    @staticmethod
    def execute(input): # keys: request, env_setting, model_setting
        global model_setting, env_setting
        # input = json.loads(input)
        env_setting = input['env_setting']
        model_setting = input['model_setting']
        (error_exists, parsed) = file_in_body_request(input['request'])
        if error_exists:
            input['request'] = parsed
        else:
            input['error'] = parsed
        return input