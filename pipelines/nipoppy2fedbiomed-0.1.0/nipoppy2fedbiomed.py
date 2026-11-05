#!/usr/bin/env python3

"""Export tabular data from a Nipoppy study for a Fed-BioMed node."""

import argparse
import fnmatch
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

MIN_NIPOPPY_VERSION = "0.4.3"
FNAME_CSV = "dataset.csv"
FNAME_JSON = "dataset_info.json"
FEDBIOMED_DATA_TYPE = "csv"
FEDBIOMED_MIN_LENGTH = 3  # for tags, name and description
TERMURL_SEX = "nb:Sex"
SEX_ENCODING = {
    "snomed:248153007": 0,  # male
    "snomed:248152002": 1,  # female
}

try:
    from nipoppy import NipoppyDataRetriever
except ImportError:
    sys.exit(
        "Error: could not import NipoppyDataRetriever. Install a compatible version of "
        f"Nipoppy, e.g. pip install 'nipoppy>={MIN_NIPOPPY_VERSION}'"
    )


def _parse_derivative(value: str) -> tuple[str, str, str]:
    # maxsplit so that the filepath pattern can contain colons
    derivative = tuple(value.split(":", 2))
    if len(derivative) != 3 or not all(derivative):
        raise argparse.ArgumentTypeError(
            f"expected PIPELINE_NAME:PIPELINE_VERSION:FILEPATH_PATTERN, got {value!r}"
        )
    return derivative


def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "nipoppy_root", type=Path, help="Root directory of the Nipoppy study."
    )
    parser.add_argument(
        "output_dir", type=Path, help="Directory to write the CSV and JSON files to."
    )
    parser.add_argument(
        "--phenotype",
        dest="phenotypes",
        action="append",
        default=[],
        metavar="TERMURL",
        help=(
            "Neurobagel TermURL of a phenotypic column in tabular/harmonized.tsv"
            " (e.g. nb:Age). Can be repeated."
        ),
    )
    parser.add_argument(
        "--derivative",
        dest="derivatives",
        action="append",
        default=[],
        type=_parse_derivative,
        metavar="PIPELINE_NAME:PIPELINE_VERSION:FILEPATH_PATTERN",
        help=(
            "Derivative TSV file to include, where FILEPATH_PATTERN is a glob pattern"
            " relative to the pipeline's derivatives directory"
            " (e.g. freesurfer:7.3.2:idp/*-aseg-volume.tsv). Can be repeated."
        ),
    )
    parser.add_argument(
        "--tag",
        dest="tags",
        action="append",
        required=True,
        help="Fed-BioMed dataset tag. Can be repeated.",
    )
    parser.add_argument(
        "--name",
        help="Fed-BioMed dataset name. Default: name of the Nipoppy root directory.",
    )
    parser.add_argument("--description", help="Fed-BioMed dataset description.")
    parser.add_argument(
        "--dataset-path",
        metavar="PATH",
        help=(
            "Dataset path written to the JSON file, as seen by the Fed-BioMed node."
            " Can start with an environment variable."
            " Default: absolute path of the CSV file."
        ),
    )
    parser.add_argument(
        "--outlier-threshold",
        type=float,
        metavar="K",
        help=(
            "Remove rows where any IDP (derivative) value is below Q1 - K*IQR"
            " or above Q3 + K*IQR. Columns with zero IQR are ignored."
            " Default: no outlier removal."
        ),
    )
    parser.add_argument(
        "--outlier-column",
        dest="outlier_columns",
        action="append",
        metavar="PATTERN",
        help=(
            "fnmatch pattern of IDP columns to check for outliers. Can be repeated."
            " Default: all IDP columns."
        ),
    )
    parser.add_argument(
        "--outlier-exclude-column",
        dest="outlier_exclude_columns",
        action="append",
        metavar="PATTERN",
        help=(
            "fnmatch pattern of IDP columns to never check for outliers,"
            " even if they match --outlier-column. Can be repeated."
        ),
    )
    return parser


def _get_outlier_mask(
    df: "pd.DataFrame", columns: list[str], threshold: float
) -> "pd.Series":
    """Return a boolean Series that is True for rows with any outlier value.

    Columns with zero IQR are ignored.
    """
    values = df[columns]
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    nonzero = iqr != 0
    values, q1, q3, iqr = values.loc[:, nonzero], q1[nonzero], q3[nonzero], iqr[nonzero]
    return ((values < q1 - threshold * iqr) | (values > q3 + threshold * iqr)).any(
        axis="columns"
    )


def _match_columns(
    columns: list[str], patterns: list[str] | None, exclude_patterns: list[str] | None
) -> list[str]:
    """Return the columns matching any pattern (all if None) and no exclude pattern."""

    def _matches(column: str, patterns: list[str]) -> bool:
        return any(fnmatch.fnmatchcase(column, pattern) for pattern in patterns)

    return [
        column
        for column in columns
        if (patterns is None or _matches(column, patterns))
        and not _matches(column, exclude_patterns or [])
    ]


def _get_zero_iqr_columns(df: "pd.DataFrame", columns: list[str]) -> list[str]:
    """Return the columns whose IQR is zero."""
    values = df[columns]
    iqr = values.quantile(0.75) - values.quantile(0.25)
    return [column for column in columns if iqr[column] == 0]


def nipoppy2fedbiomed(
    nipoppy_root: Path,
    output_dir: Path,
    phenotypes: list[str],
    derivatives: list[tuple[str, str, str]],
    tags: list[str],
    name: str | None = None,
    description: str | None = None,
    dataset_path: str | None = None,
    outlier_threshold: float | None = None,
    outlier_columns: list[str] | None = None,
    outlier_exclude_columns: list[str] | None = None,
) -> tuple[Path, Path]:
    """Write the CSV dataset and its Fed-BioMed description.

    Returns the paths to the CSV and JSON files.
    """
    if not (phenotypes or derivatives):
        raise ValueError("At least one phenotype or derivative must be specified")
    if outlier_threshold is not None:
        if outlier_threshold < 0:
            raise ValueError(
                f"Outlier threshold must be non-negative, got {outlier_threshold}"
            )
        if not derivatives:
            raise ValueError("Outlier removal requires at least one derivative")
    elif outlier_columns or outlier_exclude_columns:
        raise ValueError("Outlier columns require an outlier threshold")
    nipoppy_root = nipoppy_root.resolve()
    name = name or nipoppy_root.name
    if description is None:
        sources = [*phenotypes, *(" ".join(derivative) for derivative in derivatives)]
        description = f"Generated by nipoppy2fedbiomed (sources: {', '.join(sources)})"

    data_retriever = NipoppyDataRetriever(nipoppy_root)
    df = data_retriever.get_tabular_data(
        phenotypes=phenotypes or None,
        derivatives=[tuple(derivative) for derivative in derivatives] or None,
    )
    if TERMURL_SEX in df.columns:
        # other values become missing and are dropped below
        df[TERMURL_SEX] = df[TERMURL_SEX].map(SEX_ENCODING)
    n_rows = len(df)
    df = df.dropna(axis="index", how="any")
    if df.empty:
        raise ValueError(f"No rows without missing values in {nipoppy_root}")
    if n_dropped := n_rows - len(df):
        print(f"Dropped {n_dropped} rows with missing values")
    if outlier_threshold is not None:
        idp_columns = _match_columns(
            [column for column in df.columns if column not in phenotypes],
            outlier_columns,
            outlier_exclude_columns,
        )
        if not idp_columns:
            raise ValueError(
                "No IDP columns match the outlier column patterns"
                f" {outlier_columns} (excluding {outlier_exclude_columns})"
            )
        if zero_iqr_columns := _get_zero_iqr_columns(df, idp_columns):
            print(
                f"Skipped {len(zero_iqr_columns)} columns with zero IQR in outlier"
                f" removal: {zero_iqr_columns}"
            )
        n_rows = len(df)
        df = df.loc[~_get_outlier_mask(df, idp_columns, outlier_threshold)]
        if df.empty:
            raise ValueError(f"No rows left after outlier removal in {nipoppy_root}")
        if n_dropped := n_rows - len(df):
            print(
                f"Dropped {n_dropped} rows with outlier IDP values"
                f" (threshold: {outlier_threshold})"
            )
    if TERMURL_SEX in df.columns:
        df[TERMURL_SEX] = df[TERMURL_SEX].astype(int)

    output_dir.mkdir(parents=True, exist_ok=True)
    fpath_csv = output_dir / FNAME_CSV
    df.to_csv(fpath_csv, index=False)
    print(f"Wrote {len(df)} rows to {fpath_csv}")

    fpath_json = output_dir / FNAME_JSON
    fpath_json.write_text(
        json.dumps(
            {
                "path": dataset_path or str(fpath_csv.resolve()),
                "data_type": FEDBIOMED_DATA_TYPE,
                "name": name,
                "description": description,
                "tags": ",".join(tags),
            },
            indent=4,
        )
        + "\n"
    )
    print(f"Wrote data info to {fpath_json}")
    return fpath_csv, fpath_json


def main(argv: list[str] | None = None) -> None:
    args = _get_parser().parse_args(argv)
    try:
        nipoppy2fedbiomed(
            args.nipoppy_root,
            args.output_dir,
            phenotypes=args.phenotypes,
            derivatives=args.derivatives,
            tags=args.tags,
            name=args.name,
            description=args.description,
            dataset_path=args.dataset_path,
            outlier_threshold=args.outlier_threshold,
            outlier_columns=args.outlier_columns,
            outlier_exclude_columns=args.outlier_exclude_columns,
        )
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"Error: {e}")


if __name__ == "__main__":
    main()
