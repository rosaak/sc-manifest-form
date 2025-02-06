# Manifest Generator

A Streamlit application for generating and managing YAML manifests.

## Setup

1. Create and activate virtual environment:
```bash
uv venv -p 3.12
source .venv/bin/activate
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Running the Application

To run the Streamlit application:
```bash
streamlit run main.py
```

## Running Tests

To run the tests:
```bash
pytest test_main.py -v
```

## Features

- Create manifests with title, description, and author
- Automatic timestamp generation
- YAML file export
- Preview generated YAML
- Form validation using Pydantic
