# brainflex

Real-world neuroimaging federated learning (FL) experiment using the open neuroinformatics ecosystem described in [this preprint](https://doi.org/10.64898/2026.04.30.721944).

```{admonition} What is federated learning?
[Federated learning (FL)](https://en.wikipedia.org/wiki/Federated_learning) enables the training of machine learning models on multiple datasets without direct sharing of participant-level data.
It has use-cases in neuroimaging research (and other domains) when data-sharing is not possible due to e.g. privacy or governance concerns.
```

This website contains instructions for sites (nodes) participating in this FL experiment.
We will help you:

1. Download an [OpenNeuro](https://openneuro.org/) dataset of ~50-100 participants that has been pre-formatted into a [Nipoppy study](https://nipoppy.readthedocs.io/en/latest/) with (already processed) FreeSurfer derivatives and demographics (age and sex)
2. Use some fast (no HPC required), user-friendly [Nipoppy](https://nipoppy.readthedocs.io/en/latest/) and [Neurobagel](https://neurobagel.org/) tools to obtain **FL-ready data**
3. Deploy a [Fed-BioMed](https://fedbiomed.org/) client node and participate in the training of simple machine learning models for **brain age regression** and **biological sex classification** from FreeSurfer cortical thickness/subcortical volume data

Information about the perceived usefulness of the tools and the time required to do each step will be recorded and included in the manuscript along with the model results.

```{toctree}
---
hidden:
includehidden:
titlesonly:
caption: Instructions
---
prerequisites
initial_setup
idp_extraction
semantic_harmonization
fl_ready_dataset
fedbiomed_node_part_1
fedbiomed_node_part_2
```
