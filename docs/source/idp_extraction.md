# IDP extraction

In this step, you will use a Nipoppy pipeline to extract imaging-derived phenotypes (IDPs), such as cortical thickness and subcortical volumes, from the FreeSurfer outputs that came with your dataset.
Because every site runs the same containerized pipelines with the same configuration, **the resulting IDPs are standardized across the federation**.

```{include} _includes/working_directory.md
```

## Record start time

```bash
brainflex record idp_extraction start
```

```{important}
Starting from this step, make sure to run `brainflex record` at the beginning and end of each step, as instructed.
```

## Install pipelines

Install (i.e., download the JSON configuration files for) the FreeSurfer and FreeSurfer stats extraction pipelines:

- [`freesurfer` 7.3.2](https://zenodo.org/records/21929473): FreeSurfer has already been run on your dataset, but the configuration files still need to be installed due to a quirk in how the `fs_stats` pipeline currently works in Nipoppy.
- [`fs_stats` 0.3.0](https://zenodo.org/records/23752946): an extraction pipeline that compiles FreeSurfer outputs spread across subject directories into feature tables using [`asegstats2table`](https://surfer.nmr.mgh.harvard.edu/fswiki/asegstats2table) and [`aparcstats2table`](https://surfer.nmr.mgh.harvard.edu/fswiki/aparcstats2table).

```bash
# FreeSurfer 7.3.2
nipoppy pipeline install 21929473 --study nipoppy_study

# fs_stats 0.3.0
nipoppy pipeline install 23752946 --study nipoppy_study
```

```{note}
The `--study` option is not needed if your working directory is somewhere inside `nipoppy_study`.
```

If the [FreeSurfer 7.3.2 container image](https://hub.docker.com/r/freesurfer/freesurfer/tags?name=7.3.2) is not already on your machine, you will be prompted to download it.
Enter 'y' to accept; this can take a few (maybe 5-10) minutes and will use around 23 GB of storage.

Confirm that the pipeline have been installed correctly:

```bash
nipoppy pipeline list --study nipoppy_study
```

```{code-block}
:caption: Output
WARNING  No available bidsification pipelines
INFO     Available processing pipelines and versions
INFO             - freesurfer (7.3.2)
INFO     Available extraction pipelines and versions
INFO             - fs_stats (0.3.0)
```

### Troubleshooting: disk quota error

By default, Docker images are stored on the root disk.
If you encounter issues with disk storage quota being exceeded, you can configure Docker to use a different directory for storing data.
This can be done by following e.g. [this guide](https://www.simplified.guide/_export/xhtml/docker/change-data-directory).

## Configure the `fs_stats` pipeline with your FreeSurfer license

The `fs_stats` pipeline requires a FreeSurfer license because it runs lightweight tools that are packaged with FreeSurfer ([`asegstats2table`](https://surfer.nmr.mgh.harvard.edu/fswiki/asegstats2table) and [`aparcstats2table`](https://surfer.nmr.mgh.harvard.edu/fswiki/aparcstats2table)).
Open the study configuration file at `nipoppy_study/global_config.json` and set `FREESURFER_LICENSE_FILE` to the absolute path to your FreeSurfer license.

```{note}
If you do not already have a FreeSurfer license, fill out [this form](https://surfer.nmr.mgh.harvard.edu/registration.html) to get one.
```

```{code-block} json
:emphasize-lines: 7
    "PIPELINE_VARIABLES": {
        "BIDSIFICATION": {},
        "PROCESSING": {},
        "EXTRACTION": {
            "fs_stats": {
                "0.3.0": {
                    "FREESURFER_LICENSE_FILE": null
                }
            }
        }
    },
```

## Extract FreeSurfer statistics

```bash
nipoppy extract --pipeline fs_stats --study nipoppy_study
```

This will print a lot of output, with the final lines being this:

```{code-block}
:caption: Output
INFO     [RUN STDOUT] Exit code
INFO     [RUN STDOUT] 0
INFO     [RUN STDOUT] Error message
INFO     [RUN STDOUT]
INFO     [RUN STDOUT] Output files
INFO     [RUN STDOUT]
INFO     [RUN STDOUT] Missing files
INFO     [RUN STDOUT]
INFO     [RUN STDOUT]
INFO     Ran on the entire study 🎉🎉🎉
```

The pipeline writes a set of files to `nipoppy_study/derivatives/freesurfer/7.3.2/idp`.

```bash
tree nipoppy_study/derivatives/freesurfer/7.3.2/idp
```

```{code-block}
:caption: Output
nipoppy_study/derivatives/freesurfer/7.3.2/idp
└── fs_stats-0.3.0
    ├── fs7.3.2-aparc.a2009s-area.tsv
    ├── fs7.3.2-aparc.a2009s-meancurv.tsv
    ├── fs7.3.2-aparc.a2009s-thickness.tsv
    ├── fs7.3.2-aparc-area.tsv
    ├── fs7.3.2-aparc.DKTatlas-area.tsv
    ├── fs7.3.2-aparc.DKTatlas-meancurv.tsv
    ├── fs7.3.2-aparc.DKTatlas-thickness.tsv
    ├── fs7.3.2-aparc-meancurv.tsv
    ├── fs7.3.2-aparc-thickness.tsv
    └── fs7.3.2-aseg-volume.tsv
```

## Record end time and answer questions

```bash
brainflex record idp_extraction end
```
