"""FAERS specialized dataset client for raxtik-source-faers."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from raxtik_etl.sdk import BaseDataset


class FAERS(BaseDataset):
    """Specialized client for inspecting and querying FDA FAERS datasets."""

    source_name: str = "faers"
    default_hf_repo: str = "raxtik-org/faers-safety-database"

    def __init__(
        self,
        release: str,
        source: Optional[str] = "faers",
        package_dir: Optional[Union[str, Path]] = None,
        download_if_missing: bool = False,
        hf_repo: Optional[str] = None,
        expected_sha256: Optional[str] = None,
    ):
        super().__init__(
            release=release,
            source="faers",
            package_dir=package_dir,
            download_if_missing=download_if_missing,
            hf_repo=hf_repo or self.default_hf_repo,
            expected_sha256=expected_sha256,
        )

    @classmethod
    def from_hf(
        cls,
        release: str,
        source: Optional[str] = "faers",
        package_dir: Optional[Union[str, Path]] = None,
        hf_repo: Optional[str] = None,
        expected_sha256: Optional[str] = None,
    ) -> FAERS:
        """Loads a FAERS package, automatically downloading from Hugging Face Hub if missing locally."""
        return cls(
            release=release,
            package_dir=package_dir,
            download_if_missing=True,
            hf_repo=hf_repo,
            expected_sha256=expected_sha256,
        )

    @classmethod
    def from_source(
        cls,
        release: str,
        package_dir: Optional[Union[str, Path]] = None,
        format: str = "both",
        delete_ascii: bool = True,
        download_dir: Optional[Union[str, Path]] = None,
    ) -> FAERS:
        """Downloads FDA FAERS raw files, builds local package, and loads dataset."""
        from raxtik_source_faers import build_package

        build_package(
            release=release,
            output_dir=package_dir,
            format=format,
            delete_ascii=delete_ascii,
            download_dir=download_dir,
        )
        return cls(release=release, package_dir=package_dir)
