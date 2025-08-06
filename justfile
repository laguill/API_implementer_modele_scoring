@_:
    just --list

# try app locally
[group('docker-tools')]
demo:
    docker build --network=host -t marimo-app .
    docker run -it --rm -p 7860:7860 marimo-app
