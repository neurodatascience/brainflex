import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pandas as pd
import pytest

DPATH_PIPELINE = Path(__file__).parents[2] / "pipelines" / "nipoppy2fedbiomed-0.1.0"
FPATH_SCRIPT = DPATH_PIPELINE / "nipoppy2fedbiomed.py"
FS_VERSION = "7.3.2"
DERIVATIVES = [
    ("freesurfer", FS_VERSION, "idp/fs_stats-*/*-aseg-volume.tsv"),
    ("freesurfer", FS_VERSION, "idp/fs_stats-*/*-aparc.DKTatlas-thickness.tsv"),
]
MALE = "snomed:248153007"
FEMALE = "snomed:248152002"


def _write_tsv(fpath: Path, rows: list[dict]) -> None:
    fpath.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(fpath, sep="\t", index=False)


def _load_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    # a __pycache__ directory would make the pipeline bundle invalid
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    spec = importlib.util.spec_from_file_location("nipoppy2fedbiomed", FPATH_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    return _load_module(monkeypatch)


@pytest.fixture
def nipoppy_root(tmp_path: Path) -> Path:
    nipoppy_root = tmp_path / "ds000001"
    subprocess.run(
        ["nipoppy", "init", "--dataset", str(nipoppy_root)],
        check=True,
        capture_output=True,
    )
    _write_tsv(
        nipoppy_root / "manifest.tsv",
        [
            {
                "participant_id": participant_id,
                "visit_id": "BL",
                "session_id": "BL",
                "datatype": "['anat']",
            }
            for participant_id in ("01", "02", "03")
        ],
    )
    _write_tsv(
        nipoppy_root / "tabular" / "harmonized.tsv",
        [
            {
                "nb:ParticipantID": "01",
                "nb:SessionID": "BL",
                "nb:Age": 20.5,
                "nb:Sex": MALE,
            },
            {
                "nb:ParticipantID": "02",
                "nb:SessionID": "BL",
                "nb:Age": 30.0,
                "nb:Sex": FEMALE,
            },
            {
                "nb:ParticipantID": "03",
                "nb:SessionID": "BL",
                "nb:Age": 40.0,
                "nb:Sex": MALE,
            },
        ],
    )
    dpath_idp = (
        nipoppy_root
        / "derivatives"
        / "freesurfer"
        / FS_VERSION
        / "idp"
        / "fs_stats-0.2.0"
    )
    _write_tsv(
        dpath_idp / f"fs{FS_VERSION}-aseg-volume.tsv",
        [
            {
                "participant_id": f"sub-{p}",
                "session_id": "ses-BL",
                "Left-Hippocampus": v,
            }
            for p, v in (("01", 4000.0), ("02", 4100.0), ("03", 4200.0))
        ],
    )
    _write_tsv(
        dpath_idp / f"fs{FS_VERSION}-aparc.DKTatlas-thickness.tsv",
        [
            {"participant_id": f"sub-{p}", "session_id": "ses-BL", "lh_insula": v}
            for p, v in (("01", 2.5), ("02", 2.6), ("03", 2.7))
        ],
    )
    return nipoppy_root


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "output"


@pytest.fixture
def df() -> pd.DataFrame:
    # Q1 = 2, Q3 = 4, IQR = 2 for each column
    return pd.DataFrame(
        {
            "idp1": [1.0, 2.0, 3.0, 4.0, 5.0],
            "idp2": [1.0, 2.0, 3.0, 4.0, 5.0],
            "pheno": [1.0, 2.0, 3.0, 4.0, 5.0],
        }
    )


class TestPipelineBundle:
    def test_validate(self):
        result = subprocess.run(
            ["nipoppy", "pipeline", "validate", str(DPATH_PIPELINE)],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr


class TestImport:
    def test_nipoppy_not_installed(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setitem(sys.modules, "nipoppy", None)
        with pytest.raises(SystemExit, match="pip install 'nipoppy>=0.4.3'"):
            _load_module(monkeypatch)


class TestParseDerivative:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("freesurfer:7.3.2:idp/*.tsv", ("freesurfer", "7.3.2", "idp/*.tsv")),
            ("freesurfer:7.3.2:idp/a:b.tsv", ("freesurfer", "7.3.2", "idp/a:b.tsv")),
        ],
    )
    def test_parse_derivative(
        self, module: ModuleType, value: str, expected: tuple[str, str, str]
    ):
        assert module._parse_derivative(value) == expected

    @pytest.mark.parametrize(
        "value", ["freesurfer", "freesurfer:7.3.2", "freesurfer::idp/*.tsv"]
    )
    def test_invalid(self, module: ModuleType, value: str):
        with pytest.raises(argparse.ArgumentTypeError, match="expected PIPELINE_NAME"):
            module._parse_derivative(value)


class TestGetOutlierMask:
    def test_no_outliers(self, module: ModuleType, df: pd.DataFrame):
        # fences at -4 and 10
        mask = module._get_outlier_mask(df, ["idp1", "idp2"], 3)
        assert mask.tolist() == [False] * 5

    def test_fence_not_outlier(self, module: ModuleType, df: pd.DataFrame):
        # fences at 1 and 5: values on the fence are kept
        mask = module._get_outlier_mask(df, ["idp1", "idp2"], 0.5)
        assert mask.tolist() == [False] * 5

    @pytest.mark.parametrize("value", [-100.0, 100.0])
    def test_outlier_in_any_column(
        self, module: ModuleType, df: pd.DataFrame, value: float
    ):
        df.loc[2, "idp2"] = value
        mask = module._get_outlier_mask(df, ["idp1", "idp2"], 3)
        assert mask.tolist() == [False, False, True, False, False]

    def test_ignores_other_columns(self, module: ModuleType, df: pd.DataFrame):
        df.loc[2, "pheno"] = 100.0
        mask = module._get_outlier_mask(df, ["idp1", "idp2"], 3)
        assert mask.tolist() == [False] * 5


class TestNipoppy2fedbiomed:
    def test_nipoppy2fedbiomed(
        self, module: ModuleType, nipoppy_root: Path, output_dir: Path
    ):
        fpath_csv, fpath_json = module.nipoppy2fedbiomed(
            nipoppy_root,
            output_dir,
            phenotypes=["nb:Age", "nb:Sex"],
            derivatives=DERIVATIVES,
            tags=["brainflex", "freesurfer"],
        )
        assert fpath_csv == output_dir / "dataset.csv"
        df = pd.read_csv(fpath_csv)
        assert list(df.columns) == ["nb:Age", "nb:Sex", "Left-Hippocampus", "lh_insula"]
        assert df["nb:Age"].tolist() == [20.5, 30.0, 40.0]
        assert df["nb:Sex"].tolist() == [0, 1, 0]
        assert df["Left-Hippocampus"].tolist() == [4000.0, 4100.0, 4200.0]
        assert df["lh_insula"].tolist() == [2.5, 2.6, 2.7]

        assert fpath_json == output_dir / "dataset_info.json"
        info = json.loads(fpath_json.read_text())
        assert info == {
            "path": str(fpath_csv.resolve()),
            "data_type": "csv",
            "name": "ds000001",
            "description": info["description"],
            "tags": "brainflex,freesurfer",
        }
        assert "nb:Age" in info["description"]
        assert "freesurfer 7.3.2" in info["description"]

    def test_phenotypes_only(
        self, module: ModuleType, nipoppy_root: Path, output_dir: Path
    ):
        fpath_csv, _ = module.nipoppy2fedbiomed(
            nipoppy_root,
            output_dir,
            phenotypes=["nb:Age"],
            derivatives=[],
            tags=["tag"],
        )
        assert list(pd.read_csv(fpath_csv).columns) == ["nb:Age"]

    def test_derivatives_only(
        self, module: ModuleType, nipoppy_root: Path, output_dir: Path
    ):
        fpath_csv, _ = module.nipoppy2fedbiomed(
            nipoppy_root,
            output_dir,
            phenotypes=[],
            derivatives=DERIVATIVES,
            tags=["tag"],
        )
        assert list(pd.read_csv(fpath_csv).columns) == ["Left-Hippocampus", "lh_insula"]

    def test_name_description(
        self, module: ModuleType, nipoppy_root: Path, output_dir: Path
    ):
        _, fpath_json = module.nipoppy2fedbiomed(
            nipoppy_root,
            output_dir,
            phenotypes=["nb:Age"],
            derivatives=[],
            tags=["tag"],
            name="my-dataset",
            description="My dataset",
        )
        info = json.loads(fpath_json.read_text())
        assert info["name"] == "my-dataset"
        assert info["description"] == "My dataset"

    def test_dataset_path(
        self, module: ModuleType, nipoppy_root: Path, output_dir: Path
    ):
        _, fpath_json = module.nipoppy2fedbiomed(
            nipoppy_root,
            output_dir,
            phenotypes=["nb:Age"],
            derivatives=[],
            tags=["tag"],
            dataset_path="$NIPOPPY_ROOT/output/dataset.csv",
        )
        info = json.loads(fpath_json.read_text())
        assert info["path"] == "$NIPOPPY_ROOT/output/dataset.csv"

    def test_drops_missing(
        self,
        module: ModuleType,
        nipoppy_root: Path,
        output_dir: Path,
        capsys: pytest.CaptureFixture,
    ):
        fpath_harmonized = nipoppy_root / "tabular" / "harmonized.tsv"
        df = pd.read_csv(fpath_harmonized, sep="\t", dtype=str)
        df.loc[1, "nb:Age"] = None
        df.to_csv(fpath_harmonized, sep="\t", index=False)

        fpath_csv, _ = module.nipoppy2fedbiomed(
            nipoppy_root, output_dir, ["nb:Age", "nb:Sex"], DERIVATIVES, ["tag"]
        )
        assert pd.read_csv(fpath_csv)["nb:Age"].tolist() == [20.5, 40.0]
        assert "Dropped 1 rows with missing values" in capsys.readouterr().out

    def test_drops_other_sex(
        self,
        module: ModuleType,
        nipoppy_root: Path,
        output_dir: Path,
        capsys: pytest.CaptureFixture,
    ):
        fpath_harmonized = nipoppy_root / "tabular" / "harmonized.tsv"
        df = pd.read_csv(fpath_harmonized, sep="\t", dtype=str)
        df.loc[1, "nb:Sex"] = "snomed:32570681000036106"
        df.to_csv(fpath_harmonized, sep="\t", index=False)

        fpath_csv, _ = module.nipoppy2fedbiomed(
            nipoppy_root, output_dir, ["nb:Age", "nb:Sex"], [], ["tag"]
        )
        df = pd.read_csv(fpath_csv)
        assert df["nb:Age"].tolist() == [20.5, 40.0]
        assert df["nb:Sex"].tolist() == [0, 0]
        assert "Dropped 1 rows with missing values" in capsys.readouterr().out

    def test_outlier_removal(
        self,
        module: ModuleType,
        nipoppy_root: Path,
        output_dir: Path,
        capsys: pytest.CaptureFixture,
    ):
        # with threshold 0, only values within [Q1, Q3] are kept
        fpath_csv, _ = module.nipoppy2fedbiomed(
            nipoppy_root,
            output_dir,
            ["nb:Age", "nb:Sex"],
            DERIVATIVES,
            ["tag"],
            outlier_threshold=0,
        )
        df = pd.read_csv(fpath_csv)
        assert df["nb:Age"].tolist() == [30.0]
        assert df["nb:Sex"].tolist() == [1]
        assert "Dropped 2 rows with outlier IDP values" in capsys.readouterr().out

    def test_outlier_threshold_negative(
        self, module: ModuleType, nipoppy_root: Path, output_dir: Path
    ):
        with pytest.raises(ValueError, match="must be non-negative"):
            module.nipoppy2fedbiomed(
                nipoppy_root, output_dir, [], DERIVATIVES, ["tag"], outlier_threshold=-1
            )

    def test_outlier_threshold_without_derivatives(
        self, module: ModuleType, nipoppy_root: Path, output_dir: Path
    ):
        with pytest.raises(ValueError, match="requires at least one derivative"):
            module.nipoppy2fedbiomed(
                nipoppy_root, output_dir, ["nb:Age"], [], ["tag"], outlier_threshold=3
            )

    def test_all_missing(
        self, module: ModuleType, nipoppy_root: Path, output_dir: Path
    ):
        fpath_harmonized = nipoppy_root / "tabular" / "harmonized.tsv"
        df = pd.read_csv(fpath_harmonized, sep="\t", dtype=str)
        df["nb:Age"] = None
        df.to_csv(fpath_harmonized, sep="\t", index=False)

        with pytest.raises(ValueError, match="No rows without missing values"):
            module.nipoppy2fedbiomed(nipoppy_root, output_dir, ["nb:Age"], [], ["tag"])
        assert not output_dir.exists()

    def test_nothing_requested(
        self, module: ModuleType, nipoppy_root: Path, output_dir: Path
    ):
        with pytest.raises(ValueError, match="At least one phenotype or derivative"):
            module.nipoppy2fedbiomed(nipoppy_root, output_dir, [], [], ["tag"])


class TestMain:
    def test_main(
        self,
        module: ModuleType,
        nipoppy_root: Path,
        output_dir: Path,
        capsys: pytest.CaptureFixture,
    ):
        module.main(
            [
                str(nipoppy_root),
                str(output_dir),
                "--phenotype",
                "nb:Age",
                "--phenotype",
                "nb:Sex",
                *("--derivative", ":".join(DERIVATIVES[0])),
                *("--derivative", ":".join(DERIVATIVES[1])),
                "--tag",
                "brainflex",
                "--name",
                "my-dataset",
                "--dataset-path",
                "$NIPOPPY_ROOT/output/dataset.csv",
                *("--outlier-threshold", "3"),
            ]
        )
        assert "Wrote 3 rows" in capsys.readouterr().out
        df = pd.read_csv(output_dir / "dataset.csv")
        assert list(df.columns) == ["nb:Age", "nb:Sex", "Left-Hippocampus", "lh_insula"]
        info = json.loads((output_dir / "dataset_info.json").read_text())
        assert info["name"] == "my-dataset"
        assert info["tags"] == "brainflex"
        assert info["path"] == "$NIPOPPY_ROOT/output/dataset.csv"

    def test_tag_required(
        self, module: ModuleType, nipoppy_root: Path, output_dir: Path
    ):
        with pytest.raises(SystemExit):
            module.main([str(nipoppy_root), str(output_dir), "--phenotype", "nb:Age"])

    def test_invalid_derivative(
        self, module: ModuleType, nipoppy_root: Path, output_dir: Path
    ):
        with pytest.raises(SystemExit):
            module.main(
                [
                    str(nipoppy_root),
                    str(output_dir),
                    *("--derivative", "freesurfer:7.3.2"),
                    *("--tag", "tag"),
                ]
            )

    def test_error(self, module: ModuleType, nipoppy_root: Path, output_dir: Path):
        with pytest.raises(SystemExit, match="Error: No such file|Error: No file"):
            module.main(
                [
                    str(nipoppy_root),
                    str(output_dir),
                    *("--derivative", f"freesurfer:{FS_VERSION}:missing.tsv"),
                    *("--tag", "tag"),
                ]
            )
