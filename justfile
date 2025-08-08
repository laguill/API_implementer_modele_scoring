@_:
    just --list

# try app locally
[group('docker-tools')]
demo:
    docker build --network=host -t credit-scoring-api .
    docker run -it --rm -p 7860:7860 credit-scoring-api
