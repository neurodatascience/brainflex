# Prerequisites

## Docker and Docker Compose

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
