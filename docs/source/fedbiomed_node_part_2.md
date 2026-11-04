# Fed-BioMed node: Part 2

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

At this point, the Fed-BioMed researcher should have sent 2 training plans to your node.
This is the custom Python code needed for e.g. data loading and preprocessing.

Run this to view the training plans (need to run once for each training plan):

```bash
docker compose exec -u fedbiomed node fedbiomed node -p /fbm-node training-plan view
```

Once you are satisfied, run this to approve them (also need to run twice):

```bash
docker compose exec -u fedbiomed node fedbiomed node -p /fbm-node training-plan approve
```

Once both training plans are approved, the node is ready for training!

## Record end time

```bash
brainflex record fedbiomed_node_part_2 end
```
