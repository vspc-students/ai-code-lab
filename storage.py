import hashlib
import json
import os
import uuid

from config import DATA_FILE


def _ensure_data_file():
    """
    Make sure that the data directory and JSON storage file exist.
    """

    data_dir = os.path.dirname(DATA_FILE)

    if data_dir:
        os.makedirs(data_dir, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(
            DATA_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                [],
                file,
                ensure_ascii=False,
                indent=2,
            )


def get_or_create_participant():
    """
    Create an anonymous research participant ID.

    No name, email, phone number, or other PII is stored.
    """

    token = uuid.uuid4().hex

    return (
        "P-"
        + hashlib.sha256(
            token.encode()
        ).hexdigest()[:6].upper()
    )


def load_results():
    """
    Load all research observations from JSON storage.
    """

    _ensure_data_file()

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

            return (
                data
                if isinstance(data, list)
                else []
            )

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return []


def save_result(result):
    """
    Save one complete research observation.

    The result can contain:
        - participant information
        - task metadata
        - full task content
        - student solution
        - AI evaluation
        - future expert evaluation
    """

    if not isinstance(result, dict):
        raise ValueError(
            "Research result must be a dictionary."
        )

    results = load_results()

    results.append(result)

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2,
        )