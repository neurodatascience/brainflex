# brainflex

Real-world neuroimaging federated learning (FL) experiment using the open neuroinformatics ecosystem described in [this preprint](https://doi.org/10.64898/2026.04.30.721944).

Each site involved in the federation will:
1. Download an [OpenNeuro](https://openneuro.org/) dataset of ~100 participants that has been pre-formatted into a [Nipoppy study](https://nipoppy.readthedocs.io/en/latest/) with (already processed) FreeSurfer derivatives and demographics (age and sex)
2. Run some fast (no HPC required), user-friendly [Nipoppy](https://nipoppy.readthedocs.io/en/latest/) and [Neurobagel](https://neurobagel.org/) tools to obtain FL-ready data
3. Deploy a [Fed-BioMed](https://fedbiomed.org/) client node and participate in the training of simple machine learning models for brain age regression and biological sex classification from FreeSurfer cortical thickness/subcortical volume data

The time required to do each step will be recorded and included in the manuscript along with the model results.

```{toctree}
---
hidden:
includehidden:
titlesonly:
caption: Getting started
---
prerequisites
instructions
```
