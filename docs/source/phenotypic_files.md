# Phenotypic files

## Annotation

Download the following files to your local machine:

- `<NIPOPPY_ROOT>/tabular/pheno.tsv`
- `<NIPOPPY_ROOT>/tabular/pheno.json` (if present)

Then, go through the [Neurobagel annotation tool](https://annotate.neurobagel.org/) workflow using these files.
The following columns need to be annotated:

- Participant ID
- Session ID
- Age
- Sex

Save the annotated data dictionary to `<NIPOPPY_ROOT>/tabular/pheno_annotated.json`.

## Harmonization

From `<NIPOPPY_ROOT>`, harmonize the phenotypic data using Neurobagel's CLI:

```bash
bagel harmonize-pheno \
    --pheno tabular/pheno.tsv \
    --dictionary tabular/pheno_annotated.json \
    --output tabular/harmonized.tsv
```
