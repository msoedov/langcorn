# Langcorn: LangChain Apps api server

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
```
bash

pip install langcorn
```
## Quick Start

    Import the necessary packages and create your FastAPI app:
```
python

from fastapi import FastAPI
from langcorn import LangCorn

app = FastAPI()
langcorn = LangCorn()
```
    Load your LangChain models and pipelines:
```
python

langcorn.load_model("model_name", "path/to/model")
langcorn.load_pipeline("pipeline_name", "path/to/pipeline")
```
    Define the API endpoints for your LangChain tasks:
```
python

@app.post("/process_text")
async def process_text(text: str):
    result = await langcorn.run_pipeline("pipeline_name", text)
    return {"result": result}
```
    Run your LangCorn FastAPI server:
```
bash

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
