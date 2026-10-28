# FreeSurfer IDPs

All commands on this page assume the working directory is somewhere inside `<NIPOPPY_ROOT>`.

## Install pipelines

Install the FreeSurfer and FreeSurfer stats extraction pipelines:

```bash
# FreeSurfer
nipoppy pipeline install 21929473

# fs_stats
nipoppy pipeline install <FS_STATS_ZENODO_ID>
```

Confirm that the pipeline have been installed correctly:

```bash
nipoppy pipeline list
```

<!-- TODO expected output -->

## Configure the fs_stats pipeline with your FreeSurfer license

Open `global_config.json` and set the value of the `FREESURFER_LICENSE` pipeline variable to the path to the license on your machine.
If you do not have a FreeSurfer license, follow [these instructions](https://surfer.nmr.mgh.harvard.edu/registration.html) to get one.

## Extract FreeSurfer statistics

```bash
nipoppy extract --pipeline fs_stats --pipeline-step docker
```

This should write a set of files in ??

```bash
tree ??
```
