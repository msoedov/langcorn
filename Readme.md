# Langcorn

LangCorn is an API server that enables you to serve LangChain models and pipelines with ease, leveraging the power of FastAPI for a robust and efficient experience.

## Features

- Easy deployment of LangChain models and pipelines
- High-performance FastAPI framework for serving requests
- Scalable and robust solution for language processing applications
- Supports custom pipelines and processing
- Well-documented RESTful API endpoints
- Asynchronous processing for faster response times

## Installation

To get started with LangCorn, simply install the package using pip:
```shell

pip install langcorn
```
## Quick Start

Run your LangCorn FastAPI server:

```shell
langcorn server examples.ex1:chain examples.ex2:chain
```

or as an alternative
```shell
python -m langcorn server examples.ex1:chain examples.ex2:chain
```

Import the necessary packages and create your FastAPI app:

```python

from fastapi import FastAPI
from langcorn import create_service

app:FastAPI = create_service("examples.ex1:chain")
```

Multiple chains
```python

from fastapi import FastAPI
from langcorn import create_service

app:FastAPI = create_service("examples.ex2:chain", "examples.ex1:chain")
```

Run your LangCorn FastAPI server:
```shell

uvicorn main:app --host 0.0.0.0 --port 8000
```
Now, your LangChain models and pipelines are accessible via the LangCorn API server.
## Documentation

For more detailed information on how to use LangCorn, including advanced features and customization options, please refer to the official documentation.

## Contributing

Contributions to LangCorn are welcome! If you'd like to contribute, please follow these steps:

- Fork the repository on GitHub
- Create a new branch for your changes
- Commit your changes to the new branch
- Push your changes to the forked repository
- Open a pull request to the main LangCorn repository

Before contributing, please read the contributing guidelines.
## License

LangCorn is released under the MIT License.
