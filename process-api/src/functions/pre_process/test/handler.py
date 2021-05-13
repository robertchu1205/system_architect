class handler:
    def execute(input):
        image = input['test'][0]     
        input['test'] = image
        return input