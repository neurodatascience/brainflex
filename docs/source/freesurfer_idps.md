# FreeSurfer IDPs

## Record start time

```bash
brainflex record idp_extraction start
```

## Install pipelines

Install the FreeSurfer and FreeSurfer stats extraction pipelines:

```bash
# FreeSurfer
nipoppy pipeline install 21929473 --study nipoppy_study

# fs_stats
nipoppy pipeline install 23752946 --study nipoppy_study
```

```{note}
The `--study` option is not needed if your working directory is somewhere inside `nipoppy_study`.
```

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

## Configure the fs_stats pipeline with your FreeSurfer license

The `fs_stats` pipeline requires a FreeSurfer license because it runs lightweight tools that are packaged with FreeSurfer.
Open the study configuration file at `nipoppy_study/global_config.json` and set `FREESURFER_LICENSE_FILE` to the absolute path to your FreeSurfer license.
FreeSurfer licenses can be obtained by filling out [this form](https://surfer.nmr.mgh.harvard.edu/registration.html).

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
