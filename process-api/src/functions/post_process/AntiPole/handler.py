
class handler:
    @staticmethod
    def execute(input):
        input['image']  = input['image']
        input['kb_model']  = input['kb_model']
        input['timestamp']  = input['timestamp']
        input['loc']  = input['loc']
        input['light']  = input['light']
        input['angle']  = input['angle']
        input['roi_name']  = input['roi_name']
        input['model_name']  = input['model_name']
        input['x1']  = input['x1']
        input['x2']  = input['x2']
        input['y1']  = input['y1']
        input['y2']  = input['y2']
        input['central_crop_height']  = input['central_crop_height']
        input['central_crop_width']  = input['central_crop_width']
        input['model_result']  = input['model_result']
        return input
