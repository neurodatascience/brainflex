# Phenotypic files

## Record start time

```bash
brainflex record semantic_harmonization start
```

## Annotation

Download the following files to your local machine:

- `nipoppy_study/tabular/pheno.tsv`
- `nipoppy_study/tabular/pheno.json` (if present)

Then, go through the [Neurobagel annotation tool](https://annotate.neurobagel.org/) workflow using these files.
The following columns need to be annotated:

- Participant ID
- Session ID
- Age
- Sex

Save the annotated data dictionary to `nipoppy_study/tabular/pheno_annotated.json`.

## Harmonization

Harmonize the phenotypic data using Neurobagel's CLI:

```bash
bagel harmonize-pheno \
    --pheno nipoppy_study/tabular/pheno.tsv \
    --dictionary nipoppy_study/tabular/pheno_annotated.json \
    --output nipoppy_study/tabular/harmonized.tsv
```

The output file at `nipoppy_study/tabular/harmonized.tsv` should have 4 columns with harmonized column names and values.

```bash
head nipoppy_study/tabular/harmonized.tsv
```

<!-- markdownlint-disable MD010 -->
```{code-block}
:caption: Example output
nb:ParticipantID	nb:SessionID	nb:Sex	nb:Age
sub-1	ses-unnamed	snomed:248153007	20.0
sub-2	ses-unnamed	snomed:248152002	25.0
sub-3	ses-unnamed	snomed:248153007	30.0
sub-4	ses-unnamed	snomed:248152002	35.0
sub-5	ses-unnamed	snomed:248153007	40.0
sub-6	ses-unnamed	snomed:248152002	45.0
sub-7	ses-unnamed	snomed:248153007	50.0
sub-8	ses-unnamed	snomed:248152002	55.0
sub-9	ses-unnamed	snomed:248153007	60.0
```
<!-- markdownlint-enable MD010 -->

## Record end time and answer questions

```bash
brainflex record semantic_harmonization end
```
