#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 10/14/2016 2:00 PM
# @Author  : Jiaming Li  (jiaminli@cisco.com)
# @Site    : 
# @File    : parser.py
# @Software: PyCharm
import copy
import os
import pprint
import subprocess
import sys
from config import config


class SyntaxnetParser(object):
    def __init__(self, folder=config.syntaxnetFolder):
        self.folder=folder
        reload(sys)
        sys.setdefaultencoding('utf-8')
    def exec_from_syntax(self,string):
        os.chdir(self.folder)
        my_env = os.environ
        my_env['PYTHONIOENCODING'] = 'utf-8'
        p = subprocess.Popen([
            "syntaxnet/demo.sh"
        ], shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=my_env)
        output, err = p.communicate(string)
        return output

    def exec_from_syntax_custom(self,string,folder):
        os.chdir(self.folder)
        my_env = os.environ
        my_env['PYTHONIOENCODING'] = 'utf-8'
        p = subprocess.Popen([
            "syntaxnet/custom_parse.sh "+config.modelFolder+'/'+str(folder)
        ], shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=my_env)
        output, err = p.communicate(string)
        return output

    def parse_multi_string(self,string_list,custom=False,folder=None):
        def generate():
            string=''
            for stuff in string_list:
                if string:
                    string=string+'\n'+stuff
                else:
                    string=stuff
            return string
        if custom and folder:
            output=self.exec_from_syntax_custom(generate(),folder).split('\n')
        else:
            output=self.exec_from_syntax(generate()).split('\n')
        start=0
        result_json=[]
        try:
            for i in range(1,len(output)):
                if 'Input' in output[i]:
                    result_json.append(self.parse_string(output[start:i]))
                    start=i
                else:
                    pass
            result_json.append(self.parse_string(output[start:len(output)]))
        except Exception,e:
            print e
            result_json={"status":"error","reason":e}
        finally:
            return result_json



    def parse_string(self,format):
        def parse_col(data, json):
            if data[0] == '|':
                if 'contains' not in json[len(json) - 1]:
                    json[len(json) - 1]['contains'] = []
                json[len(json) - 1]['contains'] = parse_col(data[3:], json[len(json) - 1]['contains'])
            elif data[0] == '+--':
                builder = {"name": data[1], "pos_tag": data[2], "dep": data[3]}
                json.append(copy.copy(builder))
            elif (data[0] == '') and (data[1]=='')and (data[2]=='')and (data[3]==''):
                if 'contains' not in json[len(json) - 1]:
                    json[len(json) - 1]['contains'] = []
                json[len(json) - 1]['contains'] = parse_col(data[4:], json[len(json) - 1]['contains'])
            return json
        json = {}
        #format=['Input: The quick brown fox jumps over the lazy dog', 'Parse:', 'jumps VBZ ROOT', ' +-- fox NN nsubj', ' |   +-- The DT det', ' |   +-- quick JJ amod', ' |   +-- brown JJ amod', ' +-- over IN prep', '     +-- dog NN pobj', '         +-- the DT det', '         +-- lazy JJ amod', '']
        key = format[2].split(' ')
        json = {'name': key[0], "pos_tag": key[1], "dep": key[2], "contains": []}
        for lines in format[3:]:
            if lines=='':
                pass
            else:
                data = lines.split(' ')[1:]
                json['contains']=parse_col(data, json['contains'])
        pprint.pprint(json)
        return json