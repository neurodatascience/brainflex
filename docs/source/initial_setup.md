# Initial setup

## Installation

### Clone the starting repository

Clone the [`brainflex-node`](https://github.com/neurodatascience/brainflex-node) repository:

```bash
git clone https://github.com/neurodatascience/brainflex-node
cd brainflex-node
```

### Create virtual environment and install Python dependencies

#### With `uv`

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

## Check Docker and Docker Compose installations

Make sure your Docker installation is working:

```bash
docker run hello-world
```

This command downloads a test image and runs it in a container.
When the container runs, it prints a message like this before exiting:

```{code-block}
:caption: Output
Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

If Docker is not installed, see [these instructions](https://docs.docker.com/engine/install/) to install it and make sure to follow the [post-setup instructions](https://docs.docker.com/engine/install/linux-postinstall/).

Also make sure Docker Compose is installed:

```bash
docker compose version
```

You should get something like this:

```{code-block}
Docker Compose version vX.Y.Z
```

```{attention}
Installing Docker and Docker Compose requires `sudo` privileges.
If you do not have `sudo` privileges, you will need to ask a system admin do to the installation for you.
```

### Troubleshooting

If you get a `permission denied` error, check if your user is in the `docker` group:

```bash
groups
```

If `docker` is not in any of the groups listed, follow [this guide](https://docs.docker.com/engine/install/linux-postinstall/#add-your-user-to-the-docker-group) to add it.

## Network prerequisite

In order to join the federated network, the machine needs to have outbound UDP access to an external server (see `VPN_SERVER_ENDPOINT` in `config.env` file).
Replies from the server must also be allowed back in.

## Node configuration

```{attention}
`config.env` and `.env` are Git-ignored and should never be shared.
```

### `config.env` file

Put the `config.env` file that was shared with you in the `vpn_config/` directory:

```bash
mv <PATH_TO_CONFIG_ENV> vpn_config/config.env
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
FBM_NODE_NAME=mcgill

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

Download the OpenNeuro dataset assigned to your site, replacing `<DATASET_ID>` with its ID (beginning with `ds`):

```bash
brainflex get-data <DATASET_ID>
```

This creates a minimal Nipoppy study in `nipoppy_study` that contains all the data needed for the federated learning experiment.
