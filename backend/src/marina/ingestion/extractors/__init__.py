"""Extractors Registry for MARINA INTELLIGENCE."""

from marina.ingestion.extractors.aiff import AIFFExtractor
from marina.ingestion.extractors.base import BaseExtractor
from marina.ingestion.extractors.chennaiyin_fc import ChennaiyinFCOfficialExtractor
from marina.ingestion.extractors.isl_official import ISLOfficialExtractor
from marina.ingestion.extractors.manual_files import ManualFileExtractor
from marina.ingestion.extractors.statsbomb import StatsBombOpenDataAdapter

__all__ = [
    "BaseExtractor",
    "ISLOfficialExtractor",
    "ChennaiyinFCOfficialExtractor",
    "AIFFExtractor",
    "ManualFileExtractor",
    "StatsBombOpenDataAdapter",
]
