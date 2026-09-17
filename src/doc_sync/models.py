from dataclasses import dataclass


@dataclass(frozen=True)
class FieldContract:
    """Defines the contract for a repository-derived manifest field."""

    manifest_field: str
    authoritative_source: str
    extraction_method: str
    normalization_rule: str
    fallback_behavior: str = "Not Found"
    protected: bool = False
    sensitive: bool = False
