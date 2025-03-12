# Model Tokenizer

Microservice that tokenizes a series of input strings according to a specified model.

## New in v1.0.x

- Initial release

## Bugs, Feedback, or Enhancement Requests

Please feel free to start an issue or a discussion!

## Simple Example

```
$ ./dockerrun.sh v1.0.0
$ curl -X POST "http://localhost:8000/tokenize" -H "Content-Type: application/json" -d '{"model": "sentence-transformers/all-MiniLM-L6-v2", "text": ["Here is sentence 1!", "This is another example."]}'
{
  "tokens": [
    [
      "here", "is", "sentence", "1", "!"
    ],
    [
      "this", "is", "another", "example", "."
    ]
  ]
}
```

## Running in Docker

A Docker image is available in [Docker Hub](https://hub.docker.com/r/jchristn/modeltokenizer) under `jchristn/modeltokenizer`.  Use `docker compose up` to run within Docker Compose.  The `./models/` directory will be persisted across container restarts.

## Version History

Refer to ```CHANGELOG.md``` for version history.
