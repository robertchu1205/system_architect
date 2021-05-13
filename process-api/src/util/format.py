import json
from flask import Response

class format():
    def __init__(self):
        pass
        
    def success(**args):
        obj = {}
        obj['statusCode'] = 200
        obj['error'] = False
        obj['data'] = args.get('data', None)
        obj['message'] = args.get('message', 'OK')
        return Response(json.dumps(obj), status=200, mimetype='application/json')

    def badRequest(**args):
        obj = {}
        obj['statusCode'] =400
        obj['error'] = True
        obj['data'] = args.get('data', None)
        obj['message'] = args.get('message', 'Bad Request')
        return Response(json.dumps(obj), status=400, mimetype='application/json')

    def unAuthorized(**args):
        obj = {}
        obj['statusCode'] = 401
        obj['error'] = True
        obj['data'] = args.get('data', None)
        obj['message'] = args.get('message', 'Unauth­orized')
        return Response(json.dumps(obj), status=401, mimetype='application/json')

    def forbidden(**args):
        obj = {}
        obj['statusCode'] =403
        obj['error'] = True
        obj['data'] = args.get('data', None)
        obj['message'] = args.get('message', 'forbidden')
        return Response(json.dumps(obj), status=403, mimetype='application/json')

    def notFound(**args):
        obj = {}
        obj['statusCode'] =404
        obj['error'] = True
        obj['data'] = args.get('data', None)
        obj['message'] = args.get('message', 'Not found')
        return Response(json.dumps(obj), status=404, mimetype='application/json')

    def notAllowed(**args):
        obj = {}
        obj['statusCode'] = 405
        obj['error'] = True
        obj['data'] = args.get('data', None)
        obj['message'] = args.get('message', 'Method Not Allowed')
        return Response(json.dumps(obj), status=405, mimetype='application/json')

    def requestTimeout(**args):
        obj = {}
        obj['statusCode'] = 408
        obj['error'] = True
        obj['data'] = args.get('data', None)
        obj['message'] = args.get('message', 'Request Timeout')
        return Response(json.dumps(obj), status=408, mimetype='application/json')