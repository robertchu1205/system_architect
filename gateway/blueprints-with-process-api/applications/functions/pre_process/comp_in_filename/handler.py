import os

def parse_image_filename(filename):
    try:
        symbols = {}
        symbols.update({'filename': filename}) # CN0RM5DRWS20007600PAA00_355_0DJ01_0001_TC9401_ElecCap_270_220_NA_0.png
        possible_comps = ['AluCap', 'ElecCap', 'acpi', 'Ins', 'SATA', 'L', 'BH', 'Jumper', 'PCI', 'Aud', 'Stud', 'NI', 'DimSoc', 'CONN', 'USB', 'VGA']
        possible_bool = False
        for c in possible_comps:
            if c in filename.split('_'):
                possible_bool = True
                symbols.update({'component': c})
                filename = os.path.splitext(filename)[0] # CN0RM5DRWS20007600PAA00_355_0DJ01_0001_TC9401_ElecCap_270_220_NA_0
                splited_filename = filename.split(f'_{c}_')
                back_filename = splited_filename[-1] # 270_220_NA_0
                front_filename = splited_filename[0] # CN0RM5DRWS20007600PAA00_355_0DJ01_0001_TC9401
                symbols.update({'SN': front_filename})
                symbols.update({'PanelNo': front_filename.split('_')[0]})
                front_filename = front_filename.replace(f'{symbols["PanelNo"]}_', '') # 355_0DJ01_0001_TC9401
                symbols.update({'location': front_filename.split('_')[-1]})
                front_filename = front_filename.replace(f'_{symbols["location"]}', '') # 355_0AH01_B002
                symbols.update({'eagle': front_filename.replace('_', '')})
                symbols.update({'degree': back_filename.split('_')[0]})
                symbols.update({'capacity': back_filename.split('_')[1]})
                symbols.update({'voltage': back_filename.split('_')[2]})
                symbols.update({'index': back_filename.split('_')[3]})
        if possible_bool == False:
            symbols = {
                'filename': filename,
                'component': 'Unknown',
                'SN': 'SN',
                'PanelNo': 'PanelNo',
                'location': 'location',
                'eagle': 'eagle',
                'degree': 'degree',
                'capacity': 'capacity',
                'voltage': 'voltage',
                'index': 'index',
            }
            return symbols
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