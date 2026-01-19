# Model Tokenizer

Microservice that tokenizes a series of input strings according to a specified model.

## New in v2.0.x

- Support for chunking and commonly-used chunking input parameters such as maximum length, maximum tokens per chunk, and token overlap
- Support for tokenizing an individual string or an array of strings
- Inclusion of SHA-256 values for text and chunks in the output

## Bugs, Feedback, or Enhancement Requests

Please feel free to start an issue or a discussion!

## Simple Example - Single Text
```
$ ./dockerrun.sh v2.0.0
POST /tokenize
{
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "huggingface_api_key": null,
    "max_chunk_length": 128,
    "max_tokens_per_chunk": 5,
    "token_overlap": 2,
    "text": "The quick brown fox jumped quietly over the lazy dog sitting under the tree"
}

Response: 200/OK
{
    "text": "The quick brown fox jumped quietly over the lazy dog sitting under the tree",
    "sha256": "97f4ebc3817b6b2016e7739dc31970b8a4a8cb5f8f06281cdedb21aa49affb24",
    "tokens": [
        "the",
        "quick",
        "brown",
        "fox",
        "jumped",
        "quietly",
        "over",
        "the",
        "lazy",
        "dog",
        "sitting",
        "under",
        "the",
        "tree"
    ],
    "chunks": [
        {
            "text": "the quick brown fox jumped",
            "sha256": "3f00e8ca186729a9df3f4228c4afe4c602ed30c0618777e305292df2e3aafb6c",
            "token_count": 5
        },
        {
            "text": "fox jumped quietly over the",
            "sha256": "7b509f90eccfe72ba029a7926f0f4d247179e2f579251a4b6c03262ba6436d08",
            "token_count": 5
        },
        {
            "text": "over the lazy dog sitting",
            "sha256": "c903e6835c9d3808eda7f44c4e871e902c5deedc426c9da26ed2550b96744c4e",
            "token_count": 5
        },
        {
            "text": "dog sitting under the tree",
            "sha256": "15e756beea1d97e33d12cbcab305625ca16201f72961e4fda0ca921d018fa02c",
            "token_count": 5
        }
    ]
}
```

## Simple Example - Batch Text
```
POST /tokenize
{
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "huggingface_api_key": null,
    "max_chunk_length": 128,
    "max_tokens_per_chunk": 5,
    "token_overlap": 2,
    "texts": [
        "this is a very simple sentence",
        "hello, how's your day going today?",
        "The quick brown fox jumped quietly over the lazy dog sitting under the tree"
    ]
}

Response: 200/OK
{
    "results": [
        {
            "text": "this is a very simple sentence",
            "sha256": "32392aa65df45f53e4cc19597482acfa78060871ee9af502cc749f126d98f1c2",
            "tokens": [
                "this",
                "is",
                "a",
                "very",
                "simple",
                "sentence"
            ],
            "chunks": [
                {
                    "text": "this is a very simple",
                    "sha256": "d8dd4fdb4c422c3ae9d9b92f6b5b0ce3dd9b1c9093dab442a4c9bae561e123f2",
                    "token_count": 5
                },
                {
                    "text": "very simple sentence",
                    "sha256": "52b95013c380abee6c69f97ee42f225b5bef1d4726efd38e39076ab6175d22bb",
                    "token_count": 3
                }
            ]
        },
        {
            "text": "hello, how's your day going today?",
            "sha256": "8c09b7181ee47076617ac3fbe935d3a7f59fb53822a1302ab8131066f931f4b4",
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
            ],
            "chunks": [
                {
                    "text": "hello, how ' s",
                    "sha256": "76b5d8f4a0f83f4777ccd59cb7af8f131a8992708f0db4a69e1c3bece24efb4c",
                    "token_count": 5
                },
                {
                    "text": "' s your day going",
                    "sha256": "9f6a3cd6f10069f0e306ca035407159e318707d083f172cf131b93358c56c1fd",
                    "token_count": 5
                },
                {
                    "text": "day going today?",
                    "sha256": "cfdd1917fa90f7cd4c90c04b843e748a04dc5846bc2775900e50189e7b24da52",
                    "token_count": 4
                }
            ]
        },
        {
            "text": "The quick brown fox jumped quietly over the lazy dog sitting under the tree",
            "sha256": "97f4ebc3817b6b2016e7739dc31970b8a4a8cb5f8f06281cdedb21aa49affb24",
            "tokens": [
                "the",
                "quick",
                "brown",
                "fox",
                "jumped",
                "quietly",
                "over",
                "the",
                "lazy",
                "dog",
                "sitting",
                "under",
                "the",
                "tree"
            ],
            "chunks": [
                {
                    "text": "the quick brown fox jumped",
                    "sha256": "3f00e8ca186729a9df3f4228c4afe4c602ed30c0618777e305292df2e3aafb6c",
                    "token_count": 5
                },
                {
                    "text": "fox jumped quietly over the",
                    "sha256": "7b509f90eccfe72ba029a7926f0f4d247179e2f579251a4b6c03262ba6436d08",
                    "token_count": 5
                },
                {
                    "text": "over the lazy dog sitting",
                    "sha256": "c903e6835c9d3808eda7f44c4e871e902c5deedc426c9da26ed2550b96744c4e",
                    "token_count": 5
                },
                {
                    "text": "dog sitting under the tree",
                    "sha256": "15e756beea1d97e33d12cbcab305625ca16201f72961e4fda0ca921d018fa02c",
                    "token_count": 5
                }
            ]
        }
    ]
}
```

## Running in Docker

A Docker image is available in [Docker Hub](https://hub.docker.com/r/jchristn77/modeltokenizer) under `jchristn77/modeltokenizer`.  Use `docker compose up` to run within Docker Compose.  The `./models/` directory will be persisted across container restarts.

## Version History

Refer to ```CHANGELOG.md``` for version history.
