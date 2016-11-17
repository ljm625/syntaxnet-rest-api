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

from config import config


class SyntaxnetParser(object):
    def __init__(self, folder=config.syntaxnetFolder):
        self.folder=folder

    def exec_from_syntax(self,string):
        os.chdir(self.folder)
        p = subprocess.Popen([
            "syntaxnet/demo.sh"
        ], shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output, err = p.communicate(string)
        return output

    def exec_from_syntax_custom(self,string,folder):
        os.chdir(self.folder)
        p = subprocess.Popen([
            "syntaxnet/models/parsey_universal/parse.sh "+config.modelFolder+'/'+str(folder)
        ], shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output, err = p.communicate(string)
        return output

    def parse_multi_string(self,string_list):
        def generate():
            string=''
            for stuff in string_list:
                if string:
                    string=string+'\n'+stuff
                else:
                    string=stuff
            return string
        output=self.exec_from_syntax(generate(string_list)).split('\n')
        start=0;
        result_json=[]
        for i in range(1,len(output)):
            if 'Input' in output[i]:
                result_json.append(self.parse_string(output[start:i]))
                start=i
            else:
                pass
        result_json.append(self.parse_string(output[start:len(output)]))
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
        for lines in format[3:-1]:
            data = lines.split(' ')[1:]
            json['contains']=parse_col(data, json['contains'])
        pprint.pprint(json)
        return json


if __name__ == '__main__':
    test=SyntaxnetParser()
    test.parse_string("I am a dog")