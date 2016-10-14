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

### Special Thanks
This repo uses **brianlow's** syntaxnet docker image, also uses **tiangolo's** uwsgi+nginx+supervisord dockerfile. Special Thanks to them

If you have any questions, feel free to ask ;)
