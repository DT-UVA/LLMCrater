# LLMCrater

**Automated RO-Crate Generation for Research Data using Large Language Models**

LLMCrater is a Python tool that automatically generates [RO-Crate](https://www.researchobject.org/ro-crate/) metadata for Jupyter notebooks and associated research datasets using Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG).

## Features

- **AI-Powered Metadata Generation**: Uses local LLMs (Gemma3:12b) to intelligently create RO-Crate metadata
- **RAG-Enhanced**: Leverages Retrieval-Augmented Generation with RO-Crate specification documents for accurate metadata
- **Jupyter Notebook Support**: Automatically extracts content from Jupyter notebooks and associated data files
- **Standards Compliant**: Generates metadata following RO-Crate Metadata Specification 1.1
- **Built-in Validation**: Verifies generated metadata using the rocrate library
- **Packaging**: Creates zip files containing the complete research object
- **Zenodo Integration**: Direct upload to Zenodo with DOI assignment
- **Docker Support**: Containerized deployment available

## Installation

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai/) installed and running locally
- Required Ollama models:
  - `gemma3:12b` (LLM)
  - `nomic-embed-text:v1.5` (embeddings)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set up Ollama Models

```bash
ollama pull gemma3:12b
ollama pull nomic-embed-text:v1.5
```

### Download RO-Crate Specification Documents
```
Download the HTML files from the RO-Crate specification repository:
- https://www.researchobject.org/ro-crate/specification/1.1/

Download the JSON-LD context file:
- https://www.researchobject.org/ro-crate/specification/1.1/context.jsonld

Add both files and any other RAG documents to the `rag_sources` directory in the root.
```

## Usage

### Basic Usage

Generate RO-Crate metadata for a directory containing a Jupyter notebook:

```bash
python LLMCrater.py /path/to/your/experiment/directory
```

### Upload to Zenodo

Upload the generated RO-Crate to Zenodo sandbox:

```bash
python LLMCrater.py /path/to/your/experiment/directory --upload
```

### Publish to Zenodo

Upload and immediately publish to Zenodo (assigns DOI):

```bash
python LLMCrater.py /path/to/your/experiment/directory --upload --publish
```

## How It Works

1. **Input Analysis**: Reads Jupyter notebook content (markdown and code cells) and scans directory for all associated files

2. **RAG Processing**: 
   - Uses Chroma vector database to store RO-Crate specification documents
   - Retrieves relevant context about RO-Crate standards
   - Combines notebook content with specification knowledge

3. **Metadata Generation**: 
   - Sends structured prompts to Gemma3:12b LLM
   - Generates JSON-LD metadata following RO-Crate 1.1 specification
   - Includes dataset descriptions, file listings, software dependencies, and author information

4. **Validation & Packaging**:
   - Validates generated JSON-LD using rocrate library
   - Creates zip archive containing the complete research object

5. **Optional Upload**: Uploads to Zenodo with configurable publishing options

## Configuration

### Zenodo API Setup

Edit the Zenodo configuration in `LLMCrater.py`:

```python
ACCESS_TOKEN = "your_zenodo_api_token"  # Replace with your token

ZENODO_URL = "https://sandbox.zenodo.org/api/deposit/depositions"  # Sandbox
# ZENODO_URL = "https://zenodo.org/api/deposit/depositions"  # Production

PUBLISHER = "Doe, John" # Replace with your name
PROJECT_NAME = "Sample RO-Crate (Sandbox)" # Replace with your project name
DESCRIPTION = "This is a test RO-Crate uploaded to the Zenodo sandbox via Python." # Replace with your description
```

### Model Configuration

Modify models in `RAG.py`:

```python
EMBEDDING_MODEL = "nomic-embed-text:v1.5"
LLM_MODEL = "gemma3:12b"
```