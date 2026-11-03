# Fed-BioMed node: Part 1

We will be using [Fed-BioMed](https://fedbiomed.org/) to conduct the federated learning experiment.
See [this page](https://fedbiomed.org/federated-network/) of the Fed-BioMed website for more information about how it works.
Essentially, each site participating in the federated experiment needs to deploy a **node**, and the person responsible for running the experiment (i.e. training the models) deploys a server (**researcher** in Fed-BioMed vocabulary) to which all nodes connect to.

## Record start time

```bash
brainflex record fedbiomed_node_part_1 start
```

## Deploy the node

Run this to download the images (if needed) and start them:

```bash
docker compose up -d
```

```{code-block}
:caption: Output
[+] Running 3/3
 ✔ Network brainflex-node_default   Created
 ✔ Container brainflex-vpn-default   Healthy
 ✔ Container brainflex-node-default  Started
```

The two services are:

- `vpn`: a WireGuard VPN client that connects to the central VPN server
- `node`: the [node image](https://hub.docker.com/r/fedbiomed/node) distributed by Fed-BioMed

### Troubleshooting

By default, Docker images are stored on the root disk.
If you encounter issues with disk storage quota being exceeded, you can configure Docker to use a different directory for storing data.
This can be done by following e.g. [this guide](https://www.simplified.guide/_export/xhtml/docker/change-data-directory).

## Check Fed-BioMed node status

```bash
docker compose exec -u fedbiomed node fedbiomed node -p /fbm-node status
```

```{code-block}
:caption: Example output
:emphasize-lines: 3
# Using component located at: /fbm-node #
2026-11-03 19:27:17,690 fedbiomed INFO - Syslog configuration is disabled or not found in configuration. Disabling syslog logging.
Node status: NodeState.RUNNING
```

## Add datasets to the node

Run the two commands below to register the datasets [created by `nipoppy2fedbiomed`](fl_ready_dataset.md):

```bash
docker compose exec -u fedbiomed node fedbiomed node -p /fbm-node dataset add --file /nipoppy_study/derivatives/nipoppy2fedbiomed/0.1.0/output/age/dataset_info.json
docker compose exec -u fedbiomed node fedbiomed node -p /fbm-node dataset add --file /nipoppy_study/derivatives/nipoppy2fedbiomed/0.1.0/output/sex/dataset_info.json
```

Confirm that they have been added:

```bash
docker compose exec -u fedbiomed node fedbiomed node -p /fbm-node dataset list
```

## Share the public key with the server

Run this to get the node's public key:

```bash
docker compose logs vpn | grep 'public key'
```

This will output something like this:

```{code-block}
:caption: Output
brainflex-vpn-default  | info: wireguard public key for this peer: <PUBLIC_KEY>
```

Copy the public key (or the entire output of the previous command) and send it to us via email.

## Record end time

```bash
brainflex record fedbiomed_node_part_1 end
```

## Wait

Once all the above steps are done, wait until you hear back from the FL experiment coordinator before doing [Part 2](fedbiomed_node_part_2).
