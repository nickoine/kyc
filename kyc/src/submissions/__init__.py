from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type
    from .models import Submission, SubmissionPayload

def get_submission_model() -> "Type[Submission], Type[SubmissionPayload]":
    from .models import Submission, SubmissionPayload
    return Submission, SubmissionPayload
