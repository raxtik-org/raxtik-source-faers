"""FAERS specialized dataset client for raxtik-source-faers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from raxtik_etl.sdk import BaseDataset

from raxtik_source_faers.constants import SOURCE_NAME

if TYPE_CHECKING:
    from raxtik_etl.packaging.builder import PackageFormat


class FAERS(BaseDataset):
    """Specialized client for inspecting and querying FDA FAERS datasets."""

    source_name: str = SOURCE_NAME

    def __init__(
        self,
        data_period: str,
        source: Optional[str] = "faers",
        package_dir: Optional[Union[str, Path]] = None,
        download_if_missing: bool = False,
        hf_repo: Optional[str] = None,
        timeout: int = 120,
        revision: Optional[str] = None,
    ):
        """Initializes a FAERS dataset client for a specific quarterly period.

        Args:
            data_period: Temporal coverage period (e.g. '2004Q1').
            source: Source identifier (defaults to 'faers').
            package_dir: Local directory containing compiled packages.
            download_if_missing: If True, downloads package from Hugging Face if not found locally.
            hf_repo: Optional custom Hugging Face repo identifier.
            timeout: HTTP request timeout in seconds.
            revision: Hugging Face Git revision or branch name.

        Raises:
            ValueError: If data_period is not provided.
        """
        if not data_period:
            raise ValueError("Must provide data_period (e.g. '2004Q1')")
        super().__init__(
            data_period=data_period,
            source=source,
            package_dir=package_dir,
            download_if_missing=download_if_missing,
            hf_repo=hf_repo,
            timeout=timeout,
            revision=revision,
        )

    @property
    def release(self) -> str:
        """Backward-compatible alias for data_period.

        Returns:
            The temporal data period string.
        """
        return self.data_period

    @classmethod
    def from_hf(
        cls,
        data_period: str,
        source: Optional[str] = "faers",
        package_dir: Optional[Union[str, Path]] = None,
        hf_repo: Optional[str] = None,
        timeout: int = 120,
        revision: Optional[str] = None,
    ) -> FAERS:
        """Loads a FAERS package, automatically downloading from Hugging Face Hub if missing locally.

        Args:
            data_period: Temporal coverage period (e.g. '2004Q1').
            source: Source identifier (defaults to 'faers').
            package_dir: Local directory containing compiled packages.
            hf_repo: Optional custom Hugging Face repo identifier.
            timeout: HTTP request timeout in seconds.
            revision: Hugging Face Git revision or branch name.

        Returns:
            Connected FAERS client instance.
        """
        return cls(
            data_period=data_period,
            source=source,
            package_dir=package_dir,
            download_if_missing=True,
            hf_repo=hf_repo,
            timeout=timeout,
            revision=revision,
        )

    @classmethod
    def from_source(
        cls,
        data_period: str,
        source: Optional[str] = "faers",
        package_dir: Optional[Union[str, Path]] = None,
        format: Union[PackageFormat, str] = "both",
        delete_ascii: bool = True,
        download_dir: Optional[Union[str, Path]] = None,
    ) -> FAERS:
        """Downloads FDA FAERS raw files, builds local package, and loads dataset.

        Args:
            data_period: Temporal coverage period (e.g. '2004Q1').
            source: Source identifier (defaults to 'faers').
            package_dir: Destination folder for built package.
            format: Package format to build ('both', 'duckdb', or 'parquet').
            delete_ascii: Whether to remove raw ASCII files after packaging.
            download_dir: Temporary download directory for raw archives.

        Returns:
            Connected FAERS client instance.
        """
        from raxtik_source_faers.builder import build_package

        build_package(
            data_period=data_period,
            output_dir=package_dir,
            format=format,
            delete_ascii=delete_ascii,
            download_dir=download_dir,
        )
        return cls(data_period=data_period, source=source, package_dir=package_dir)
