# Langcorn

LangCorn is an API server that enables you to serve LangChain models and pipelines with ease, leveraging the power of FastAPI for a robust and efficient experience.

<p>
<img alt="GitHub Contributors" src="https://img.shields.io/github/contributors/msoedov/langcorn" />
<img alt="GitHub Last Commit" src="https://img.shields.io/github/last-commit/msoedov/langcorn" />
<img alt="" src="https://img.shields.io/github/repo-size/msoedov/langcorn" />
<img alt="GitHub Issues" src="https://img.shields.io/github/issues/msoedov/langcorn" />
<img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/msoedov/langcorn" />
<img alt="Github License" src="https://img.shields.io/github/license/msoedov/langcorn" />
</p>

## Features

- Easy deployment of LangChain models and pipelines
- Ready to use auth functionality
- High-performance FastAPI framework for serving requests
- Scalable and robust solution for language processing applications
- Supports custom pipelines and processing
- Well-documented RESTful API endpoints
- Asynchronous processing for faster response times

## 📦 Installation

To get started with LangCorn, simply install the package using pip:

```shell

pip install langcorn
```

## ⛓️ Quick Start

Example LLM chain ex1.py

```python

import os

from langchain import LLMMathChain, OpenAI

os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "sk-********")

llm = OpenAI(temperature=0)
chain = LLMMathChain(llm=llm, verbose=True)
```

Run your LangCorn FastAPI server:

```shell
langcorn server examples.ex1:chain


[INFO] 2023-04-18 14:34:56.32 | api:create_service:75 | Creating service
[INFO] 2023-04-18 14:34:57.51 | api:create_service:85 | lang_app='examples.ex1:chain':LLMChain(['product'])
[INFO] 2023-04-18 14:34:57.51 | api:create_service:104 | Serving
[INFO] 2023-04-18 14:34:57.51 | api:create_service:106 | Endpoint: /docs
[INFO] 2023-04-18 14:34:57.51 | api:create_service:106 | Endpoint: /examples.ex1/run
INFO:     Started server process [27843]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8718 (Press CTRL+C to quit)
```

or as an alternative

```shell
python -m langcorn server examples.ex1:chain

```

Run multiple chains

```shell
python -m langcorn server examples.ex1:chain examples.ex2:chain


[INFO] 2023-04-18 14:35:21.11 | api:create_service:75 | Creating service
[INFO] 2023-04-18 14:35:21.82 | api:create_service:85 | lang_app='examples.ex1:chain':LLMChain(['product'])
[INFO] 2023-04-18 14:35:21.82 | api:create_service:85 | lang_app='examples.ex2:chain':SimpleSequentialChain(['input'])
[INFO] 2023-04-18 14:35:21.82 | api:create_service:104 | Serving
[INFO] 2023-04-18 14:35:21.82 | api:create_service:106 | Endpoint: /docs
[INFO] 2023-04-18 14:35:21.82 | api:create_service:106 | Endpoint: /examples.ex1/run
[INFO] 2023-04-18 14:35:21.82 | api:create_service:106 | Endpoint: /examples.ex2/run
INFO:     Started server process [27863]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8718 (Press CTRL+C to quit)
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

or

```python
from fastapi import FastAPI
from langcorn import create_service

app: FastAPI = create_service(
    "examples.ex1:chain",
    "examples.ex2:chain",
    "examples.ex3:chain",
    "examples.ex4:sequential_chain",
    "examples.ex5:conversation",
    "examples.ex6:conversation_with_summary",
    "examples.ex7_agent:agent",
)

```

Run your LangCorn FastAPI server:

```shell

uvicorn main:app --host 0.0.0.0 --port 8000
```

Now, your LangChain models and pipelines are accessible via the LangCorn API server.

## Docs

Automatically served FastAPI doc
[Live example](https://langcorn-ift9ub8zg-msoedov.vercel.app/docs#/) hosted on vercel.

![](https://res.cloudinary.com/dq0w2rtm9/image/upload/c_pad,b_auto:predominant,fl_preserve_transparency/v1681817836/Screen_Shot_2023-04-18_at_14.36.00_ms2thb.jpg?_s=public-apps)

## Auth

It possible to add a static api token auth by specifying `auth_token`

```shell
python langcorn server examples.ex1:chain examples.ex2:chain --auth_token=api-secret-value
```

or

```python
app:FastAPI = create_service("examples.ex1:chain", auth_token="api-secret-value")
```

## Custom API KEYs

```shell
POST http://0.0.0.0:3000/examples.ex6/run
X-LLM-API-KEY: sk-******
Content-Type: application/json
```

## Handling memory

```json
{
  "history": "string",
  "input": "What is brain?",
  "memory": [
    {
      "type": "human",
      "data": {
        "content": "What is memory?",
        "additional_kwargs": {}
      }
    },
    {
      "type": "ai",
      "data": {
        "content": " Memory is the ability of the brain to store, retain, and recall information. It is the capacity to remember past experiences, facts, and events. It is also the ability to learn and remember new information.",
        "additional_kwargs": {}
      }
    }
  ]
}

```

Response:

```json
{
  "output": " The brain is an organ in the human body that is responsible for controlling thought, memory, emotion, and behavior. It is composed of billions of neurons that communicate with each other through electrical and chemical signals. It is the most complex organ in the body and is responsible for all of our conscious and unconscious actions.",
  "error": "",
  "memory": [
    {
      "type": "human",
      "data": {
        "content": "What is memory?",
        "additional_kwargs": {}
      }
    },
    {
      "type": "ai",
      "data": {
        "content": " Memory is the ability of the brain to store, retain, and recall information. It is the capacity to remember past experiences, facts, and events. It is also the ability to learn and remember new information.",
        "additional_kwargs": {}
      }
    },
    {
      "type": "human",
      "data": {
        "content": "What is brain?",
        "additional_kwargs": {}
      }
    },
    {
      "type": "ai",
      "data": {
        "content": " The brain is an organ in the human body that is responsible for controlling thought, memory, emotion, and behavior. It is composed of billions of neurons that communicate with each other through electrical and chemical signals. It is the most complex organ in the body and is responsible for all of our conscious and unconscious actions.",
        "additional_kwargs": {}
      }
    }
  ]
}
```

## LLM kwargs

To override the default LLM params per request

```shell
POST http://0.0.0.0:3000/examples.ex1/run
X-LLM-API-KEY: sk-******
X-LLM-TEMPERATURE: 0.7
X-MAX-TOKENS: 256
X-MODEL-NAME: gpt5
Content-Type: application/json
```

## Documentation

For more detailed information on how to use LangCorn, including advanced features and customization options, please refer to the official documentation.

## 👋 Contributing

Contributions to LangCorn are welcome! If you'd like to contribute, please follow these steps:

- Fork the repository on GitHub
- Create a new branch for your changes
- Commit your changes to the new branch
- Push your changes to the forked repository
- Open a pull request to the main LangCorn repository

Before contributing, please read the contributing guidelines.

## License

LangCorn is released under the MIT License.
