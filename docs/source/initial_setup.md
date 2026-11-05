# Initial setup

## Installation

### Clone the starting repository

Clone and enter the [`brainflex-node`](https://github.com/neurodatascience/brainflex-node) repository:

```bash
git clone https://github.com/neurodatascience/brainflex-node
cd brainflex-node
```

### Create virtual environment and install Python dependencies

#### With `uv`

To install `uv`: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/) (`sudo` privileges **not** needed).

```bash
uv venv --python 3.14
source .venv/bin/activate
uv pip install -r requirements.txt
```

#### With `venv`

Make sure your Python version is between **3.11 and 3.14 inclusive**.

```bash
python3 -m venv .venv --prompt brainflex-node
source .venv/bin/activate
pip install -r requirements.txt
```

#### With `conda`

```bash
conda create --name brainflex-node python=3.14
conda activate brainflex-node
pip install -r requirements.txt
```

## Verify installation

The above step installs three packages/tools:

1. `bagel`: [Neurobagel CLI](https://pypi.org/project/bagel/)
2. `nipoppy`: [Nipoppy CLI](https://pypi.org/project/nipoppy/)
3. `brainflex`: Custom helper tool for this project

You can verify that they were installed successfully by running `<TOOL_NAME> --help`, where `<TOOL_NAME>` is one of `bagel`, `nipoppy`, and `brainflex`.
This should print information about the CLI commands and options.

## Initial survey

Answer a short survey about your prior experience with Nipoppy, Neurobagel and Fed-BioMed:

```bash
brainflex initial-survey
```

## Node configuration

```{attention}
The content of `config.env` and `.env` should not be openly shared.
```

### `config.env` file

Put the `config.env` file that was shared with you in the `vpn_config/` directory:

```bash
mv <PATH_TO_CONFIG_ENV_FILE> vpn_config/config.env
```

### `.env` file

Create a `.env` file from the provided template:

```bash
cp .env.example .env
```

Edit `.env` and set:

- `FBM_NODE_NAME` to the value of `FEDBIOMED_NODEID` in the `config.env` file that was shared with you
- `CONTAINER_UID` and `CONTAINER_GID` to the output of `id -u` and `id -g`, respectively

:::{admonition} Example `.env` file content
:class: dropdown

```{code-block}
:emphasize-lines: 15,19,20
#
# docker-compose.yml variables
# Copy to `.env` and edit as needed
#

# Fed-BioMed version of the node image
# Must be the same version as the researcher and the VPN server
FBM_CONTAINER_VERSION_TAG=6.4.1

# Unique ID for this instance, among all the instances deployed on this machine
# (used in container names)
FBM_CONTAINER_INSTANCE_ID=default

# Fed-BioMed node name, as shown to the researcher
FBM_NODE_NAME=mcgill-ds123456

# Host user and group owning the files in `fbm-node`
# Set to the output of `id -u` and `id -g`. If unset, files are owned by UID/GID 2101
CONTAINER_UID=1002
CONTAINER_GID=1001

# Relative or absolute path to the Nipoppy study associated with this node
NIPOPPY_ROOT=./nipoppy_study

# Researcher address on the VPN (Fed-BioMed VPN defaults)
#FBM_RESEARCHER_IP=10.222.0.2
#FBM_RESEARCHER_PORT=50051

# Options passed to `fedbiomed node start`, eg `--gpu`
#FBM_NODE_START_OPTIONS=

# Node security settings (Fed-BioMed defaults shown)
FBM_SECURITY_FORCE_SECURE_AGGREGATION=True
FBM_SECURITY_TRAINING_PLAN_APPROVAL=True
FBM_SECURITY_ALLOW_DEFAULT_TRAINING_PLANS=False
FBM_SECURITY_ALLOW_PREPROC=True
FBM_SECURITY_ALLOW_FEDERATED_ANALYTICS=True
```

:::

## Data download

Download the OpenNeuro dataset assigned to your site, replacing `<DATASET_ID>` with its ID.
Your dataset ID is the second part of the `FBM_NODE_NAME` variable you just set in your `.env` file, beginning with `ds` (e.g. `ds123456` in the example `.env` file above).

```bash
brainflex get-data <DATASET_ID>
```

The command may run for a few (maybe 3-5) minutes.
It will create a minimal Nipoppy study in a new directory, `nipoppy_study`, that contains all the data needed for the federated learning experiment.

```{note}
To save disk space and download time, only the files needed for this experiment are downloaded: the raw imaging files are empty placeholders, and the FreeSurfer outputs only include the `stats` and `scripts` directories.
```
