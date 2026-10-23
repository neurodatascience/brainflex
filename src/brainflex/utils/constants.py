"""Constants."""

# project
DATA_DIRNAME = "data"
BRAINFLEX_DIRNAME = ".brainflex"
STATUS_LOG_FILENAME = "status_log.tsv"
COL_TIMESTAMP = "timestamp"
COL_STEP = "step"
COL_STATUS = "status"
STATUS_LOG_COLUMNS = (COL_TIMESTAMP, COL_STEP, COL_STATUS)

# check
INTERNET_CHECK_URL = "https://www.google.com"
CHECK_TIMEOUT = 10  # seconds

# get-data
OPENNEURO_BUCKET = "openneuro.org"
OPENNEURO_REGION = "us-east-1"
DERIVATIVES_BUCKET = "openneuro-derivatives"
DERIVATIVES_REGION = "us-west-2"
FREESURFER_PREFIX = "fmriprep/{dataset_id}-fmriprep/sourcedata/freesurfer"
FREESURFER_SUBDIRS = ("stats", "scripts")
FREESURFER_BUILD_STAMP = "scripts/build-stamp.txt"
FREESURFER_PIPELINE_NAME = "freesurfer"
BIDS_SUBJECT_PREFIX = "sub-"
BIDS_SESSION_PREFIX = "ses-"
PARTICIPANTS_FILENAME = "participants.tsv"
PHENO_FILENAME = "pheno.tsv"
COL_PARTICIPANT_ID = "participant_id"
