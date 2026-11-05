# Fed-BioMed node: Part 1

We will be using [Fed-BioMed](https://fedbiomed.org/) to conduct the federated learning experiment.
See [this page](https://fedbiomed.org/federated-network/) of the Fed-BioMed website for more information about how it works.
Essentially, each site participating in the federated experiment needs to deploy a **node**, and the person responsible for running the experiment (i.e. training the models) deploys a server (**researcher** in Fed-BioMed vocabulary) to which all nodes connect to.

During training, the researcher sends experiment-specific code (a *training plan*) to all nodes.
Nodes use this code to train a local model, then send model weights to the researcher (subject-level data never leave the node).
The researcher aggregates the set of all weights to produce a global model, which can be sent back to the nodes for further training.

```{include} _includes/working_directory.md
```

## Record start time

```bash
brainflex record fedbiomed_node_part_1 start
```

## Deploy the node

Run this to download the images (about 18 GB in total) and start them:

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

The download can take a couple of (maybe 5–10) minutes, depending on your Internet connection.

The two services are:

- `vpn`: a WireGuard VPN client that connects to the central VPN server
- `node`: the [node image](https://hub.docker.com/r/fedbiomed/node) distributed by Fed-BioMed

### Troubleshooting: disk quota error

If you run out of disk space and have already tried changing the Docker data directories [as previously described](idp_extraction.md#troubleshooting-disk-quota-error), you can remove the FreeSurfer image downloaded in the [IDP extraction step](idp_extraction), as it is not needed anymore.

1. List your images:

    ```bash
    docker image ls --filter reference=freesurfer/freesurfer:7.3.2
    ```

    ```{code-block}
    :caption: Example output
    IMAGE                         ID             DISK USAGE   CONTENT SIZE   EXTRA
    freesurfer/freesurfer:7.3.2   e04a8cf308a8       22.5GB         6.88GB
    ```

    Note the `ID` that corresponds to the `freesurfer/freesurfer:7.3.2` image.

2. Remove the image

    ```bash
    docker image rm <IMAGE_ID>
    ```

3. If you get an error about a container (running or stopped) still using the image, find it:

    ```bash
    docker container ls --all --filter ancestor=freesurfer/freesurfer:7.3.2
    ```

    Note its `ID`.
    Stop it if it's running, then remove it:

    ```bash
    docker container stop <CONTAINER ID>
    docker container rm <CONTAINER ID>
    ```

    Then remove the image:

    ```bash
    docker image rm <IMAGE_ID>
    ```

## Check Fed-BioMed node status

Run this to confirm that the node is running:

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

### Troubleshooting: permission error

If the command fails with a permission error like this:

```{code-block}
PermissionError: [Errno 13] Permission denied: '/fbm-node/log'
```

check that `CONTAINER_UID` and `CONTAINER_GID` in your `.env` file match the output of `id -u` and `id -g` (see [Initial setup](initial_setup.md#env-file)), then restart the containers:

```bash
docker compose down
docker compose up -d
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

You should see a table like this:

```{code-block}
:caption: Example output
Listing your data available
name    data_type    tags                  description                                                                                                                                                                              path                                                                       shape               dataset_id                                    dataset_parameters
------  -----------  --------------------  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------  -------------------------------------------------------------------------  ------------------  --------------------------------------------  --------------------
age     csv          ['brainflex', 'age']  Generated by nipoppy2fedbiomed (sources: nb:Age, nb:Sex, freesurfer 7.3.2 idp/fs_stats-*/fs7.3.2-aparc.DKTatlas-thickness.tsv, freesurfer 7.3.2 idp/fs_stats-*/fs7.3.2-aseg-volume.tsv)  /nipoppy_study/derivatives/nipoppy2fedbiomed/0.1.0/output/age/dataset.csv  {'csv': [80, 131]}  dataset_f555e76c-e98c-46f4-81f8-6936edc5a004  {}
sex     csv          ['brainflex', 'sex']  Generated by nipoppy2fedbiomed (sources: nb:Age, nb:Sex, freesurfer 7.3.2 idp/fs_stats-*/fs7.3.2-aparc.DKTatlas-thickness.tsv, freesurfer 7.3.2 idp/fs_stats-*/fs7.3.2-aseg-volume.tsv)  /nipoppy_study/derivatives/nipoppy2fedbiomed/0.1.0/output/sex/dataset.csv  {'csv': [80, 131]}  dataset_4b7addc7-37c4-404c-a530-279554e3237d  {}
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
We will register it on the central VPN server so that your node can join the federated network.

```{note}
Sharing the public key is safe and necessary for establishing a connection with the VPN server.
```

## Record end time

```bash
brainflex record fedbiomed_node_part_1 end
```

## Wait

Once all the above steps are done, wait until you hear back from the FL experiment coordinator before doing [Part 2](fedbiomed_node_part_2).
