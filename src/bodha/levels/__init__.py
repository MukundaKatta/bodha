"""Level adapters for different reading levels."""

from bodha.levels.elementary import ElementaryAdapter
from bodha.levels.middle import MiddleSchoolAdapter
from bodha.levels.general import GeneralPublicAdapter
from bodha.levels.expert import ExpertAdapter

__all__ = ["ElementaryAdapter", "MiddleSchoolAdapter", "GeneralPublicAdapter", "ExpertAdapter"]
