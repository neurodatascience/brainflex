"""Constants."""

# project
NIPOPPY_STUDY_DIRNAME = "nipoppy_study"
BRAINFLEX_DIRNAME = ".brainflex"

# surveys
COL_QUESTION = "question"
COL_ANSWER = "answer"
SURVEY_COLUMNS = (COL_QUESTION, COL_ANSWER)
LIKERT_CHOICES = ("1", "2", "3", "4", "5")
FAMILIARITY_LABELS = (
    "I have never heard of it before this project",
    "I have heard of it but never used",
    "I have used but only with example/toy data",
    "I have used with real data but not regularly",
    "I use it regularly / It is one of my go-to tools",
)
BACKUP_TIMESTAMP_FORMAT = "%Y%m%dT%H%M%S"

# initial-survey
INITIAL_SURVEY_FILENAME = "initial_survey.tsv"
INITIAL_SURVEY_QUESTIONS = tuple(
    f"How familiar are you with {tool}?"
    for tool in ("Nipoppy", "Neurobagel", "Fed-BioMed")
)

# record
TIMESTAMPS_FILENAME = "timestamps.tsv"
COL_TIMESTAMP = "timestamp"
COL_STEP = "step"
COL_STATUS = "status"
TIMESTAMPS_COLUMNS = (COL_TIMESTAMP, COL_STEP, COL_STATUS)
STEP_SURVEY_FILENAME = "step_survey.tsv"
STEP_SURVEY_COLUMNS = (COL_STEP, *SURVEY_COLUMNS)
QUESTION_TOOL_EASIER_TEMPLATE = "Did {tool} make it easier to do this step?"
TOOLS_EASIER_CHOICES = ("yes", "no", "unsure")
QUESTION_TIME_WITHOUT_TOOL_TEMPLATE = (
    "How long do you think this would have taken without {tool}?"
)
TIME_WITHOUT_TOOLS_CHOICES = ("<1h", "1-4h", "4-8h", "1-3d", "3-7d", ">7d")
QUESTION_NOTES = "Notes/feedback"

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
