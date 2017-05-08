#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 10/14/2016 2:00 PM
# @Author  : Jiaming Li  (jiaminli@cisco.com)
# @Site    : 
# @File    : dragnn_parser.py
# @Software: PyCharm
import copy
import os
import pprint
import subprocess
import sys

import re

from config import config


import os
import tensorflow as tf
from dragnn.protos import spec_pb2
from dragnn.python import graph_builder
from dragnn.python import spec_builder
from dragnn.python import load_dragnn_cc_impl  # This loads the actual op definitions
from dragnn.python import render_parse_tree_graphviz
from dragnn.python import visualization
from google.protobuf import text_format
from syntaxnet import load_parser_ops  # This loads the actual op definitions
from syntaxnet import sentence_pb2
from syntaxnet.ops import gen_parser_ops
from tensorflow.python.platform import tf_logging as logging


class SyntaxnetParser(object):
    def __init__(self,model_folder, folder=config.syntaxnetFolder):
        self.folder=folder
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.segmenter_model = self.load_model("{}/segmenter".format(model_folder), "spec.textproto", "checkpoint")
        self.parser_model = self.load_model(model_folder, "parser_spec.textproto", "checkpoint")

    def load_model(self,base_dir, master_spec_name, checkpoint_name):
        # Read the master spec
        master_spec = spec_pb2.MasterSpec()
        with open(os.path.join(base_dir, master_spec_name), "r") as f:
            text_format.Merge(f.read(), master_spec)
        spec_builder.complete_master_spec(master_spec, None, base_dir)
        logging.set_verbosity(logging.WARN)  # Turn off TensorFlow spam.

        # Initialize a graph
        graph = tf.Graph()
        with graph.as_default():
            hyperparam_config = spec_pb2.GridPoint()
            builder = graph_builder.MasterBuilder(master_spec, hyperparam_config)
            # This is the component that will annotate test sentences.
            annotator = builder.add_annotation(enable_tracing=True)
            builder.add_saver()  # "Savers" can save and load models; here, we're only going to load.

        sess = tf.Session(graph=graph)
        with graph.as_default():
            # sess.run(tf.global_variables_initializer())
            # sess.run('save/restore_all', {'save/Const:0': os.path.join(base_dir, checkpoint_name)})
            builder.saver.restore(sess, os.path.join(base_dir, checkpoint_name))

        def annotate_sentence(sentence):
            with graph.as_default():
                return sess.run([annotator['annotations'], annotator['traces']],
                                feed_dict={annotator['input_batch']: [sentence]})

        return annotate_sentence

    def annotate_text(self,text):
        sentence = sentence_pb2.Sentence(
            text=text,
            token=[sentence_pb2.Token(word=text, start=-1, end=-1)]
        )

        # preprocess
        with tf.Session(graph=tf.Graph()) as tmp_session:
            char_input = gen_parser_ops.char_token_generator([sentence.SerializeToString()])
            preprocessed = tmp_session.run(char_input)[0]
        segmented, _ = self.segmenter_model(preprocessed)

        annotations, traces = self.parser_model(segmented[0])
        assert len(annotations) == 1
        assert len(traces) == 1
        return sentence_pb2.Sentence.FromString(annotations[0])

    def exec_from_syntax(self,string):
        os.chdir(self.folder)
        my_env = os.environ
        my_env['PYTHONIOENCODING'] = 'utf-8'
        p = subprocess.Popen([
            "syntaxnet/demo.sh"
        ], shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=my_env)
        output, err = p.communicate(string)
        return output
    """
    1       Google  _       ADJ     JJ      Number=Sing|fPOS=PROPN++NNP     3       nsubj   _       _
    2       is      _       VERB    VBZ     Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|fPOS=VERB++VBZ  3       cop     _       _
    3       awesome!        _       NOUN    NN      Degree=Pos|fPOS=ADJ++JJ 0       ROOT    _       _
    """

    def parse_notree_string(self,output_list):
        '''Used for parsing the output of a none tree stuff..'''
        # lines=len(output_list)
        output = []
        for i in range(0, len(output_list['output'])):
            output.append({})
        i = 0

        for stuff in output_list['output']:
            # print(stuff)
            output[i] = stuff
            i = i + 1
            # output[i]['category']=stuff['category']
            # output[i]['pos_tag'] = stuff[4]
            # for cell in stuff[5].split('|'):
            #     info=cell.split('=')
            #     output[int(stuff[0]) - 1][info[0]]=info[1]
            # output[int(stuff[0]) - 1]['parent'] = int(stuff[6])-1
            # output[int(stuff[0]) - 1]['dep'] = stuff[7]
        # Start to merge it to a tree
        structured_tree = {}
        print(output)

        def merge_to_target(target, output, tree):
            for i in range(0, len(output_list['output'])):
                if 'head' in output[i] and output[i]['head'] == target:
                    del output[i]['head']
                    if 'contains' in tree:
                        tree['contains'].append(output[i])
                    else:
                        tree['contains'] = [output[i]]
                    merge_to_target(i, output, tree['contains'][tree['contains'].index(output[i])])

        for i in range(0, len(output_list['output'])):
            if 'head' in output[i] and output[i]['head'] == -1:
                structured_tree = output[i]
                del output[i]['head']
                merge_to_target(i, output, structured_tree)
        return structured_tree

    def parse_string_from_dragnn(self,sentence):
        result = self.annotate_text(sentence)

        def parse_attribute(input, todo_dict):
            pattern = re.compile(r'\"[^"]*\"')
            result = list(pattern.findall(input))
            #print(result)
            return_val = {}
            for i in range(0, len(result), 2):
                print(filter(None, result[i].split('"')))
                todo_dict[filter(None, result[i].split('"'))[0].lower()] = filter(None, result[i + 1].split('"'))[0]
            return todo_dict

        return_dict = {}
        return_dict['input'] = result.text
        output = []
        for stuff in result.token:
            tmpdict = {}
            tmpdict['word'] = stuff.word
            tmpdict['label'] = stuff.label
            tmpdict['dep'] = stuff.label
            tmpdict['break_level'] = stuff.break_level
            tmpdict['category'] = stuff.category
            tmpdict['head'] = stuff.head
            tmpdict = parse_attribute(str(stuff.tag), tmpdict)

            # tmp fix for getting back the pos_tag
            tmpdict['pos_tag']=tmpdict['fpos'].split('++')[1]

            output.append(tmpdict)
        return_dict['output'] = output
        return return_dict




    # def exec_from_syntax_custom(self,string,folder):
    #     os.chdir(self.folder)
    #     my_env = os.environ
    #     my_env['PYTHONIOENCODING'] = 'utf-8'
    #     p = subprocess.Popen([
    #         "syntaxnet/custom_parse.sh "+config.modelFolder+'/'+str(folder)
    #     ], shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=my_env)
    #     output, err = p.communicate(string)
    #     return output

    def parse_multi_string(self,string_list,tree=False):
        def generate():
            string=''
            for stuff in string_list:
                if string:
                    string=string+'\n'+stuff
                else:
                    string=stuff
            return string

        try:
            return_list=[]
            for string in string_list:
                if tree:
                    result=self.parse_notree_string(self.parse_string_from_dragnn(string))
                else: result=self.parse_string_from_dragnn(string)
                return_list.append(result)
            result_json=return_list
        except Exception as e:
            print(e)
            result_json={"status":"error","reason":e}
        finally:
            return result_json


    # def parse_multi_string_custom(self,string_list,folder):
    #     def generate():
    #         string=''
    #         for stuff in string_list:
    #             if string:
    #                 string=string+'\n'+stuff
    #             else:
    #                 string=stuff
    #         return string
    #     output=filter(None,self.exec_from_syntax_custom(generate(),folder).split('\n'))
    #     start=0
    #     result_json=[]
    #     try:
    #         for i in range(1,len(output)):
    #             if output[i][0:2]=='1\t':
    #                 result_json.append(self.parse_notree_string(output[start:i]))
    #                 start=i
    #             else:
    #                 pass
    #         result_json.append(self.parse_notree_string(output[start:len(output)]))
    #     except Exception as e:
    #         print(e)
    #         result_json={"status":"error","reason":e}
    #     finally:
    #         return result_json



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