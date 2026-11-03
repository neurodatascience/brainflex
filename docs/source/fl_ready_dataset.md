# FL-ready dataset

## Record start time

```bash
brainflex record fl_ready_data start
```

## Pipeline installation

Install the Nipoppy-to-Fed-BioMed conversion pipeline:

```bash
nipoppy pipeline install 23753437 --study nipoppy_study
```

The pipeline should now be listed when you run:

```bash
nipoppy pipeline list --study nipoppy_study
```

```{code-block}
:caption: Output
WARNING  No available bidsification pipelines
INFO     Available processing pipelines and versions
INFO             - freesurfer        (7.3.2)
INFO             - nipoppy2fedbiomed (0.1.0)
INFO     Available extraction pipelines and versions
INFO             - fs_stats (0.3.0)
```

## Dataset extraction

Combine the FreeSurfer IDPs and harmonized phenotypic data into a Fed-BioMed dataset:

```bash
nipoppy process --pipeline nipoppy2fedbiomed --pipeline-step age --study nipoppy_study
nipoppy process --pipeline nipoppy2fedbiomed --pipeline-step sex --study nipoppy_study
```

For each of the prediction tasks (brain age regression and biological sex classification), this will write a CSV file (the Fed-BioMed dataset) and a JSON file used to register it on the [Fed-BioMed node](fedbiomed_node_part_1.md).

```bash
tree nipoppy_study/derivatives/nipoppy2fedbiomed
```

```{code-block}
:caption: Output
nipoppy_study/derivatives/nipoppy2fedbiomed
└── 0.1.0
    └── output
        ├── age
        │   ├── dataset.csv
        │   └── dataset_info.json
        └── sex
            ├── dataset.csv
            └── dataset_info.json
```

## Record end time and answer questions

```bash
brainflex record fl_ready_data end
```
