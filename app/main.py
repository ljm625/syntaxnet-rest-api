#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 10/14/2016 2:00 PM
# @Author  : Jiaming Li  (jiaminli@cisco.com)
# @Site    :
# @File    : dragnn_parser.py
# @Software: PyCharm
from flask import Flask
from flask_restful import Resource, Api, reqparse

import dragnn_parser
from config import config
parse_handler=None



app = Flask(__name__)
api = Api(app)

class SyntaxQuery(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('strings', required=True, type=list, help='string is required field, you should input a list of strings', location='json')
        self.reqparse.add_argument('tree', required=False, type=bool, default=False,
                                   location='json')
        self.reqparse.add_argument('syntax_folder', required=False, type=str, default=config.syntaxnetFolder,
                                   location='json')
        super(SyntaxQuery, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        if parse_handler==None:
            return {"result":"fail", "reason":"Please initialize the model first!"}, 400
        #parse = parser.SyntaxnetParser(segmenter_model,parser_model,folder=args['syntax_folder'])
        try:
            return parse_handler.parse_multi_string(args['strings'],tree=args['tree'])
        except Exception as e:
            return {'result': 'fail', "reason": e}, 400

# class SyntaxModelQuery(Resource):
#     def __init__(self):
#         self.reqparse = reqparse.RequestParser()
#         self.reqparse.add_argument('strings', required=True, type=list, help='string is required field, you should input a list of strings', location='json')
#         self.reqparse.add_argument('syntax_folder', required=False, type=str, default=config.syntaxnetFolder,
#                                    location='json')
#         super(SyntaxModelQuery, self).__init__()
#
#     def post(self,folder):
#         args = self.reqparse.parse_args()
#         parse = parser.SyntaxnetParser(folder=args['syntax_folder'])
#         try:
#             return parse.parse_multi_string_custom(args['strings'],folder=folder)
#         except Exception, e:
#             return {'result': 'fail', "reason": e}, 400


class SyntaxModelLoading(Resource):
    def __init__(self):
        super(SyntaxModelLoading, self).__init__()

    def get(self,folder):
        #args = self.reqparse.parse_args()
        try:
            global parse_handler
            parse_handler=dragnn_parser.SyntaxnetParser("{}/{}".format(config.modelFolder, folder))
            #segmenter_model = load_model("{}/{}/segmenter".format(config.modelFolder,folder), "spec.textproto", "checkpoint")
            #parser_model = load_model("{}/{}".format(config.modelFolder,folder), "parser_spec.textproto", "checkpoint")
            return {"result":"success"},200
        except Exception as e:
            return {'result': 'fail', "reason": e}, 400




api.add_resource(SyntaxQuery, '/api/v1/query')
api.add_resource(SyntaxModelLoading, '/api/v1/use/<string:folder>')
#api.add_resource(SyntaxModelQuery, '/api/v1/query/<string:folder>')



if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0',
            port=9000)