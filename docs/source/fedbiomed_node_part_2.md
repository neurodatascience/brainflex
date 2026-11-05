# Fed-BioMed node: Part 2

```{attention}
Only start this part after the FL experiment coordinator has told you that your public key has been registered and that the training plans have been sent to your node.
```

In this step, you will check that your node can reach the researcher, then review and approve the code that will be run on your machine.

```{include} _includes/working_directory.md
```

## Record start time

```bash
brainflex record fedbiomed_node_part_2 start
```

## Check VPN connection

Check that the VPN server and the researcher are reachable:

```bash
scripts/vpn_status
```

```{code-block}
:caption: Example output
** Checking docker containers & VPN access: vpn node
- container vpn is running
- container node is running
- pinging VPN server (10.220.0.1) from container vpn -> OK
- pinging researcher (10.222.0.2) from container vpn -> OK
```

## View and approve the training plans

A Fed-BioMed *training plan* is the custom Python code that will be run on your node, e.g. for data loading, preprocessing and model definition.

At this point, the Fed-BioMed researcher process should have sent 2 training plans to your node (via the VPN connection), one for each prediction task (brain age regression and biological sex classification).
Your node is configured to only run approved code, so you will need to review and approve them before training can start.

Run this to view the training plans (need to run once for each training plan):

```bash
docker compose exec -u fedbiomed node fedbiomed node -p /fbm-node training-plan view
```

This prints the code of the training plan to the terminal.

Once you are satisfied, run this to approve them (also need to run twice):

```bash
docker compose exec -u fedbiomed node fedbiomed node -p /fbm-node training-plan approve
```

Once both training plans are approved, the node is ready for training!

## Record end time

```bash
brainflex record fedbiomed_node_part_2 end
```

## Share data about setup timing

Timing information and your answers to the initial survey and step-specific questions have been saved to TSV files under the `.brainflex` directory:

```bash
tree .brainflex
```

```{code-block}
:caption: Output
.brainflex/
├── initial_survey.tsv
├── step_survey.tsv
└── timestamps.tsv
```

Take a look at them, make edits as needed, and send them to us via email.

## Next

Once all nodes are set up and have approved the training plans, the researcher will launch the federated learning experiment through the network.
There is nothing else to do on your side for the moment.
Just make sure to:

- Leave the containers running
- Keep the machine turned on and connected to the internet until the end of the experiment (estimated to be 1-2 months)

You can check that the containers are still running with:

```bash
docker compose ps
```

We will keep you updated on the progress of the experiment and manuscript.
Thank you for participating!
