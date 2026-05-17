#Pensjon-Lakehouse/pensjon/di/dependencies.py
"""
Dependency injection / composition root.

Tilsvarer dependencies.js i værappen.
To datakilder: befolkning (07459) og lønn/sysselsetting (11654).
"""

from pensjon.datasource.befolkning_datasource import BefolkningDataSource
from pensjon.datasource.lonn_datasource import LonnSysselsettingDataSource

from pensjon.repository.befolkning_repository import BefolkningRepository
from pensjon.repository.arbeidsmarked_repository import LonnSysselsettingRepository

from pensjon.usecase.pensjon_usecases import (GetPensionAgeShareUseCase, GetNaeringProfilUseCase,)


class Dependencies:
    """Composition root – oppretter hele objektgrafen."""

    def __init__(self):
        # DataSources
        self.befolkning_ds = BefolkningDataSource()
        self.lonn_syss_ds = LonnSysselsettingDataSource()

        # Repositories
        self.befolkning_repo = BefolkningRepository(self.befolkning_ds)
        self.lonn_syss_repo = LonnSysselsettingRepository(self.lonn_syss_ds)

        # Use Cases
        self.get_pension_age_share = GetPensionAgeShareUseCase(self.befolkning_repo)
        self.get_naering_profil = GetNaeringProfilUseCase(self.lonn_syss_repo)
