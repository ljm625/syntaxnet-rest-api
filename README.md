# Syntaxnet Rest API
This is a simple Rest API for Google Syntaxnet. It parse the string with syntaxnet and return a json for you

The server uses Flask-restful / uwsgi and nginx, so it should be okay for multi query at the same time ( To be tested)

**The Version you're checking is using the latest DRAGNN mode, which is way more faster than the original one!**


### Usage
docker run -p 9000:9000 -v **/test_folder**:/models -d ljm625/syntaxnet-rest-api:dragnn

Look here for detail: https://github.com/tensorflow/models/blob/master/syntaxnet/g3doc/conll2017/README.md

Download the conll2017 from here: https://drive.google.com/file/d/0BxpbZGYVZsEeSFdrUnBNMUp1YzQ/view?usp=sharing

Then extract the file and put the **language folder** you're using into a folder. (we use **/test_folder** here)

execute the command like this:

docker run -p 9000:9000 -v **/test_folder**:/models -d ljm625/syntaxnet-rest-api:dragnn

then GET to **http://localhost:9000/api/v1/use/*the_folder_name***

for example, I am using English package, and the folder we extracted is called English, so the path is like **/test_folder/English**, and the url should be **http://localhost:9000/api/v1/use/English**

The command above will load the model and let you able to use the module

then POST to **http://localhost:9000/api/v1/query**


The Body of the POST is a json consisting following info:
```json
{
   "strings": ["Google is awesome!","Syntaxnet is Cool"]
   "tree": true/false
}
```
The **TREE option** determines whether the output format is like a tree or just some lists, please check the demo below


and you should expect a response **instantly**.

#### Response with tree:false
```json
[
  {
    "input": "Google is awesome!",
    "output": [
      {
        "category": "",
        "head": 2,
        "word": "Google",
        "break_level": 0,
        "fPOS": "PROPN++NNP",
        "Number": "Sing",
        "label": "nsubj"
      },
      {
        "category": "",
        "head": 2,
        "word": "is",
        "Mood": "Ind",
        "break_level": 1,
        "fPOS": "AUX++VBZ",
        "Number": "Sing",
        "label": "cop",
        "Person": "3",
        "Tense": "Pres",
        "VerbForm": "Fin"
      },
      {
        "category": "",
        "head": -1,
        "word": "awesome",
        "Degree": "Pos",
        "break_level": 1,
        "fPOS": "ADJ++JJ",
        "label": "root"
      },
      {
        "category": "",
        "head": 2,
        "word": "!",
        "break_level": 0,
        "fPOS": "PUNCT++.",
        "label": "punct"
      }
    ]
  },
  {
    "input": "Syntaxnet is Cool",
    "output": [
      {
        "category": "",
        "head": 2,
        "word": "Syntaxnet",
        "break_level": 0,
        "fPOS": "NOUN++NN",
        "Number": "Sing",
        "label": "nsubj"
      },
      {
        "category": "",
        "head": 2,
        "word": "is",
        "Mood": "Ind",
        "break_level": 1,
        "fPOS": "AUX++VBZ",
        "Number": "Sing",
        "label": "cop",
        "Person": "3",
        "Tense": "Pres",
        "VerbForm": "Fin"
      },
      {
        "category": "",
        "head": -1,
        "word": "Cool",
        "Degree": "Pos",
        "break_level": 1,
        "fPOS": "ADJ++JJ",
        "label": "root"
      }
    ]
  }
]
```

#### Response with tree:true
```json
[
  {
    "category": "",
    "word": "awesome",
    "Degree": "Pos",
    "break_level": 1,
    "contains": [
      {
        "category": "",
        "word": "Google",
        "break_level": 0,
        "fPOS": "PROPN++NNP",
        "Number": "Sing",
        "label": "nsubj"
      },
      {
        "category": "",
        "word": "is",
        "Mood": "Ind",
        "break_level": 1,
        "fPOS": "AUX++VBZ",
        "Number": "Sing",
        "label": "cop",
        "Person": "3",
        "Tense": "Pres",
        "VerbForm": "Fin"
      },
      {
        "category": "",
        "word": "!",
        "break_level": 0,
        "fPOS": "PUNCT++.",
        "label": "punct"
      }
    ],
    "fPOS": "ADJ++JJ",
    "label": "root"
  },
  {
    "category": "",
    "word": "Cool",
    "Degree": "Pos",
    "break_level": 1,
    "contains": [
      {
        "category": "",
        "word": "Syntaxnet",
        "break_level": 0,
        "fPOS": "NOUN++NN",
        "Number": "Sing",
        "label": "nsubj"
      },
      {
        "category": "",
        "word": "is",
        "Mood": "Ind",
        "break_level": 1,
        "fPOS": "AUX++VBZ",
        "Number": "Sing",
        "label": "cop",
        "Person": "3",
        "Tense": "Pres",
        "VerbForm": "Fin"
      }
    ],
    "fPOS": "ADJ++JJ",
    "label": "root"
  }
]```


Feel free to try different languages using the prebuilt models :D

### Special Thanks
This repo uses uses **tiangolo's** uwsgi+nginx+supervisord dockerfile. Special Thanks to him

### Updates
2017/02/28:
Using another method for fetching the info from syntaxnet engine, so you can get lots of info using custom model than before :D

2017/02/26:
Fix the issue with the UTF8 encoding, so non-lantern language are supported

2016/11/18:
Update the logic for multi sentence query so it should faster now

2016/11/17:
Updated the syntaxnet repo with the latest code, with working parser_universal and muti-language support.


If you have any questions, feel free to ask in the discussion part ;)
