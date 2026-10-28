# Initial setup

## Installation

Clone the [`brainflex-node`](https://github.com/neurodatascience/brainflex-node) repository:

```bash
git clone https://github.com/neurodatascience/brainflex-node
cd brainflex-node
```

Then install the requirements (in a fresh virtual environment):

### With `uv`

```bash
uv venv --python 3.11
uv pip install -r requirements.txt
```

### With `venv`

### With `conda`

## Project initialization

Initialize the project in the current directory:

```bash
brainflex init
```

## Prerequisites check

Check that the prerequisites are satisfied:

```bash
brainflex check
```

Any check marked as `FAIL` must be fixed before continuing.
Checks marked as `WARN` are not required.

## Data download

Download the OpenNeuro dataset assigned to your site, replacing `<DATASET_ID>` with its ID (beginnign with `ds`):

```bash
brainflex get-data <DATASET_ID>
```

This creates a Nipoppy study in `data/<DATASET_ID>`. In the rest of the instructions, this directory is referred to as `<NIPOPPY_ROOT>`.
