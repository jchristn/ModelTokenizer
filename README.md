# Model Tokenizer

Microservice that tokenizes a series of input strings according to a specified model.

## New in v1.0.x

- Initial release

## Bugs, Feedback, or Enhancement Requests

Please feel free to start an issue or a discussion!

## Simple Example - Single Text
```
$ ./dockerrun.sh v1.0.0
$ curl -X POST "http://localhost:8000/tokenize" -H "Content-Type: application/json" -d '{"model": "sentence-transformers/all-MiniLM-L6-v2", "huggingface_api_key": null, "text": "this is a very simple sentence" }'

Response: 200/OK
{
  "text": "this is a very simple sentence",
  "tokens": [
    "this",
    "is",
    "a",
    "very",
    "simple",
    "sentence"
  ]
}
```

## Simple Example - Batch Text
```
$ ./dockerrun.sh v1.0.0
$ curl -X POST "http://localhost:8000/tokenize" -H "Content-Type: application/json" -d '{"model": "sentence-transformers/all-MiniLM-L6-v2", "huggingface_api_key": null, "texts": [ "this is a very simple sentence", "hello, how's your day going today?" ] }'

Response: 200/OK
{
  "results": [
    {
      "text": "this is a very simple sentence",
      "tokens": [
        "this",
        "is",
        "a",
        "very",
        "simple",
        "sentence"
      ]
    },
    {
      "text": "hello, how's your day going today?",
      "tokens": [
        "hello",
        ",",
        "how",
        "'",
        "s",
        "your",
        "day",
        "going",
        "today",
        "?"
      ]
    }
  ]
}
```

## Running in Docker

A Docker image is available in [Docker Hub](https://hub.docker.com/r/jchristn/modeltokenizer) under `jchristn/modeltokenizer`.  Use `docker compose up` to run within Docker Compose.  The `./models/` directory will be persisted across container restarts.

## Version History

Refer to ```CHANGELOG.md``` for version history.
