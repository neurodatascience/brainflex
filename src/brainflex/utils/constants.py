"""Constants."""

# project
DATA_DIRNAME = "data"
BRAINFLEX_DIRNAME = ".brainflex"
STATUS_LOG_FILENAME = "status_log.tsv"

# record
BACKUP_TIMESTAMP_FORMAT = "%Y%m%dT%H%M%S"
COL_TIMESTAMP = "timestamp"
COL_STEP = "step"
COL_STATUS = "status"
COL_NOTES = "notes"
STATUS_LOG_COLUMNS = (COL_TIMESTAMP, COL_STEP, COL_STATUS, COL_NOTES)

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
PARTICIPANTS_JSON_FILENAME = "participants.json"
PHENO_FILENAME = "pheno.tsv"
PHENO_JSON_FILENAME = "pheno.json"
COL_PARTICIPANT_ID = "participant_id"
COL_SESSION_ID = "session_id"
