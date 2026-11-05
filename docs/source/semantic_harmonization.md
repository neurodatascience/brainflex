# Semantic harmonization

In this step, you will use the [Neurobagel annotation tool](https://annotate.neurobagel.org/) to map your dataset's phenotypic variables (age and sex) from their original naming/encoding conventions to standardized terms.
You will then create a semantically harmonized copy of your phenotypic data, where column names and values use a **standardized vocabulary** that is shared with all other sites.

```{include} _includes/working_directory.md
```

## Record start time

```bash
brainflex record semantic_harmonization start
```

## Annotate phenotypic TSV file

The [Neurobagel annotation tool](https://annotate.neurobagel.org/) runs in a web browser.
You need to upload:

- `nipoppy_study/tabular/pheno.tsv` in the **Data Table** box
- `nipoppy_study/tabular/pheno.json` in the **Data Dictionary** box (optional, only if present)

If you are working on a remote machine, you will need to first copy these files to the computer where you use your web browser (e.g. with `scp`).

Then, go through the annotation tool workflow at [https://annotate.neurobagel.org/](https://annotate.neurobagel.org/) using these files.

```{tip}
Click on the "How to use this page?" buttons in the annotation tool for guidance.
```

The following standardized variables **need to be assigned**:

- Participant ID
- Session ID
- Age
- Sex

You can ignore the "Diagnosis" and "Assessment Tool" standardized variables, as well as the "Data Description" step near the end of the workflow.

Save/copy the annotated data dictionary to `nipoppy_study/tabular/pheno_annotated.json` on the machine with the rest of the data.

## Create harmonized phenotypic TSV file

Harmonize the phenotypic data using the Neurobagel CLI:

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
sub-1	ses-1	snomed:248153007	20.0
sub-2	ses-1	snomed:248152002	25.0
sub-3	ses-1	snomed:248153007	30.0
sub-4	ses-1	snomed:248152002	35.0
sub-5	ses-1	snomed:248153007	40.0
sub-6	ses-1	snomed:248152002	45.0
sub-7	ses-1	snomed:248153007	50.0
sub-8	ses-1	snomed:248152002	55.0
sub-9	ses-1	snomed:248153007	60.0
```
<!-- markdownlint-enable MD010 -->

```{note}
You may have `ses-unnamed` in the `nb:SessionID` column.
This is because some OpenNeuro datasets do not have explicit session names, in which case Nipoppy will use `unnamed` as the session ID.
```

## Record end time and answer questions

```bash
brainflex record semantic_harmonization end
```
