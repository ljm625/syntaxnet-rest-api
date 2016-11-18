# Syntaxnet Rest API
This is a simple Rest API for Google Syntaxnet. It parse the string with syntaxnet and return a json for you

The server uses Flask-restful / uwsgi and nginx, so it should be okay for multi query at the same time ( To be tested)

### Usage
docker run -p 9000:9000 -d ljm625/syntaxnet-rest-api

then use curl to POST **http://localhost:9000/api/v1/query**

The Body of the POST is a json consisting following info:
```json
{
   "strings": ["Google is awesome!","Syntaxnet is Cool","..."] 
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

for example, I am using English package, so the url is **http://localhost:9000/api/v1/query/English**

The Body of the POST is a json consisting following info:
```json
{
   "strings": ["Google is awesome!","Syntaxnet is Cool","..."] 
}
```

and you should expect a response using the custom model.

```json
[
  {
    "pos_tag": "NOUN++NN",
    "dep": "ROOT",
    "contains": [
      {
        "pos_tag": "ADJ++JJ",
        "dep": "nsubj",
        "name": "Google"
      },
      {
        "pos_tag": "VERB++VBZ",
        "dep": "cop",
        "name": "is"
      }
    ],
    "name": "awesome!"
  },
  {
    "pos_tag": "PROPN++NNP",
    "dep": "ROOT",
    "contains": [
      {
        "pos_tag": "PROPN++NNP",
        "dep": "nsubj",
        "name": "Syntaxnet"
      },
      {
        "pos_tag": "VERB++VBZ",
        "dep": "cop",
        "name": "is"
      }
    ],
    "name": "Cool"
  }
]
```

Feel free to try different languages using the prebuilt models :D

### Special Thanks
This repo uses uses **tiangolo's** uwsgi+nginx+supervisord dockerfile. Special Thanks to him

### Updates
2016/11/18:
Update the logic for multi sentence query so it should faster now

2016/11/17:
Updated the syntaxnet repo with the latest code, with working parser_universal and muti-language support.


If you have any questions, feel free to ask in the discussion part ;)
