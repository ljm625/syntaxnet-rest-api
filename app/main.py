from flask import Flask
from flask_restful import Resource, Api, reqparse

import parser
from config import config

app = Flask(__name__)
api = Api(app)

class SyntaxQuery(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('strings', required=True, type=list, help='string is required field, you should input a list of strings', location='json')
        self.reqparse.add_argument('syntax_folder', required=False, type=str, default=config.syntaxnetFolder,
                                   location='json')
        super(SyntaxQuery, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        parse = parser.SyntaxnetParser(folder=args['syntax_folder'])
        try:
            ret_val=[]
            for string in args['strings']:
                ret_val.append(parse.parse_string(string))
            return ret_val
        except Exception, e:
            return {'result': 'fail', "reason": e}, 400

api.add_resource(SyntaxQuery, '/api/v1/query')


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0',
            port=9000)