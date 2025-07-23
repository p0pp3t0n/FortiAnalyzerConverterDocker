# FortiLog CSV Converter

This is a very simple docker container that will host an app to convert FortiLogs into a CSV format.
It uses the python code from <https://github.com/N4SOC/fortilogcsv>

## Installation

The Dockerfile is self-explanatory, it will expose the application on 0.0.0.0 port 5000.

```
git clone https://github.com/p0pp3t0n/FortiAnalyzerConverterDocker
docker-compose build
docker-compose up -d
```

## How to use

1. Upload or drag a drop a file in the website.
2. Profit

## Things to change

1. Change the secret key in the app.py
