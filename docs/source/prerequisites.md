# Prerequisites

## Docker and Docker Compose

In order to deploy a node for the federated learning experiment, you will need [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/).
Docker is a tool that runs software inside containers, which are self-contained packages that bundle a program with all its dependencies.
Docker Compose builds on Docker to start and manage several containers together from a single configuration file (`docker-compose.yml`).

Check if Docker is installed and working:

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

````{note}
You can check your Docker version with:

```bash
docker version --format '{{.Server.Version}}'
```

```{code-block}
:caption: Example output
29.7.0
```

Any recent version of Docker should work.
These instructions were tested with Docker 29.1.3, 29.6.2 and 29.7.0.
````

If Docker is not installed, see [these instructions](https://docs.docker.com/engine/install/) to install it and make sure to follow the [post-setup instructions](https://docs.docker.com/engine/install/linux-postinstall/).

```{attention}
Installing Docker and Docker Compose requires `sudo` privileges.
If you do not have `sudo` privileges, you will need to ask a sys admin or your IT department to do the installation for you.
```

Also make sure Docker Compose is installed:

```bash
docker compose version
```

You should get something like this:

```{code-block}
:caption: Example output
Docker Compose version v5.3.1
```

```{note}
Any recent version of Docker Compose should work.
These instructions were tested with versions 2.37.1 and 5.3.1.
```

If Docker Compose is not installed, follow [these instructions](https://docs.docker.com/compose/install/linux/#install-using-the-repository) (or ask a sys admin) to install it.

### Troubleshooting: permission error

If you get a `permission denied` error, check if your user is in the `docker` group:

```bash
groups
```

If `docker` is not in any of the groups listed, follow [this guide](https://docs.docker.com/engine/install/linux-postinstall/#add-your-user-to-the-docker-group) (or ask your sys admin) to add it.

## Networking

Each site connects to the federated network through a [WireGuard](https://www.wireguard.com/) virtual private network (VPN).

In order to join the federated network, your machine needs outbound UDP access to an external server, on the host and port given by `VPN_SERVER_ENDPOINT` in the `config.env` file. No inbound ports need to be opened.

```{note}
[UDP](https://en.wikipedia.org/wiki/User_Datagram_Protocol) is one of the two main protocols used to send data over the internet (the other being [TCP](https://en.wikipedia.org/wiki/Transmission_Control_Protocol)). Outbound UDP traffic is allowed by default on many institutional networks.
```
