# Syntaxnet Rest API
This is a simple Rest API for Google Syntaxnet. It parse the string with syntaxnet and return a json for you

The server uses Flask-restful / uwsgi and nginx, so it should be okay for multi query at the same time ( To be tested)

**Please switch to dragnn branch if you have performance consideration, also it's newer :D**

### Usage
docker run -p 9000:9000 -d ljm625/syntaxnet-rest-api

then use curl to POST **http://localhost:9000/api/v1/query**

The Body of the POST is a json consisting following info:
```json
{
   "strings": ["Google is awesome!","Syntaxnet is Cool"]
}
```

and the expect output is like:
```json
[
  {
    "pos_tag": "JJ",
    "dep": "ROOT",
    "contains": [
      {
        "pos_tag": "NNP",
        "dep": "nsubj",
        "name": "Google"
      },
      {
        "pos_tag": "VBZ",
        "dep": "cop",
        "name": "is"
      }
    ],
    "name": "awesome"
  }
]
```
### Using parsey_universal
Look here for detail: https://github.com/tensorflow/models/blob/master/syntaxnet/universal.md

After you download the model, unzip into to folder as you like (we use **/test_folder** here)

execute the command like this:

docker run -p 9000:9000 -v **/test_folder**:/models -d ljm625/syntaxnet-rest-api

then POST to **http://localhost:9000/api/v1/query/*the_folder_name***

for example, I am using English package, and the folder we extracted is called English, so the path is like **/test_folder/English**, and the url should be **http://localhost:9000/api/v1/query/English**

The Body of the POST is a json consisting following info:
```json
{
   "strings": ["Google is awesome!","Syntaxnet is Cool"]
}
```

and you should expect a response using the custom model.

```json
[
  {
    "pos_tag": "NN",
    "Degree": "Pos",
    "name": "awesome!",
    "dep": "ROOT",
    "contains": [
      {
        "pos_tag": "JJ",
        "name": "Google",
        "dep": "nsubj",
        "fPOS": "PROPN++NNP",
        "Number": "Sing",
        "pos": "ADJ"
      },
      {
        "pos_tag": "VBZ",
        "Mood": "Ind",
        "dep": "cop",
        "fPOS": "VERB++VBZ",
        "Number": "Sing",
        "pos": "VERB",
        "Person": "3",
        "Tense": "Pres",
        "VerbForm": "Fin",
        "name": "is"
      }
    ],
    "fPOS": "ADJ++JJ",
    "pos": "NOUN"
  },
  {
    "pos_tag": "NNP",
    "name": "Cool",
    "dep": "ROOT",
    "contains": [
      {
        "pos_tag": "NNP",
        "name": "Syntaxnet",
        "dep": "nsubj",
        "fPOS": "PROPN++NNP",
        "Number": "Sing",
        "pos": "PROPN"
      },
      {
        "pos_tag": "VBZ",
        "Mood": "Ind",
        "dep": "cop",
        "fPOS": "VERB++VBZ",
        "Number": "Sing",
        "pos": "VERB",
        "Person": "3",
        "Tense": "Pres",
        "VerbForm": "Fin",
        "name": "is"
      }
    ],
    "fPOS": "PROPN++NNP",
    "Number": "Sing",
    "pos": "PROPN"
  }
]
```

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
