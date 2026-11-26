# Updating the node

When a new version of [`brainflex-node`](https://github.com/neurodatascience/brainflex-node) is released, follow these steps to update to the latest version (**|node_version|**).

```{include} _includes/working_directory.md
```

## Update the code

First, check whether you created a work branch:

```bash
git branch --show-current
```

If this prints `work` (or another branch name you created):

```bash
git fetch origin tag |node_version| --no-tags
git merge --no-edit |node_version|
```

If this prints nothing (you skipped the optional `git switch -c work` step in [Initial setup](initial_setup.md)):

```bash
git fetch origin tag |node_version| --no-tags
git switch --detach |node_version|
```

To confirm the update worked, run:

```bash
git describe --tags
```

If you have no commits of your own, this prints `|node_version|`.
If you merged into a branch that had your own commits, it prints something like `|node_version|-2-gabc1234`, which is also fine.

## Update Python dependencies

With your virtual environment (or `conda` environment) activated, reinstall the dependencies in case they changed:

```bash
pip install -r requirements.txt  # or: uv pip install -r requirements.txt
```

## Restart the Fed-BioMed node

Only do this if you have already started the node (see [Fed-BioMed node: Part 1](fedbiomed_node_part_1.md)):

```bash
docker compose down
docker compose up -d
```
