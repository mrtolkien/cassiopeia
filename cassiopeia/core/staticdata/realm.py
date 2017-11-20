from typing import Dict, Union

from merakicommons.cache import lazy_property
from merakicommons.container import searchable

from ...data import Region, Platform
from ..common import CoreData, CassiopeiaGhost, provide_default_region, ghost_load_on
from ...dto.staticdata import realm as dto


##############
# Data Types #
##############


class RealmData(CoreData):
    _dto_type = dto.RealmDto
    _renamed = {"lg": "legacyMode", "dd": "latestDataDragon", "l": "language", "n": "latestVersions",
                "profileiconmax": "maxProfileIconId", "v": "version", "css": "cssVersion"}

    #@property
    #def max_profile_icon_id(self) -> int:
    #    """Special behavior number identifying the largest profile icon ID that can be used under 500. Any profile icon that is requested between this number and 500 should be mapped to 0."""
    #    return self._dto["profileiconmax"]

    #@property
    #def store(self) -> str:
    #    """Additional API data drawn from other sources that may be related to Data Dragon functionality."""
    #    return self._dto["store"]

    #@property
    #def version(self) -> str:
    #    """Current version of this file for this realm."""
    #    return self._dto["v"]

    #@property
    #def cdn(self) -> str:
    #    """The base CDN URL."""
    #    return self._dto["cdn"]

    #@property
    #def css_version(self) -> str:
    #    """Latest changed version of Dragon Magics CSS file."""
    #    return self._dto["css"]


##############
# Core Types #
##############


@searchable({})
class Realms(CassiopeiaGhost):
    _data_types = {RealmData}

    @provide_default_region
    def __init__(self, region: Union[Region, str] = None):
        kwargs = {"region": region}
        super().__init__(**kwargs)

    def __get_query__(self):
        return {"region": self.region, "platform": self.platform}

    @lazy_property
    def region(self) -> Region:
        """The region for this realm."""
        return Region(self._data[RealmData].region)

    @lazy_property
    def platform(self) -> Platform:
        """The platform for this realm."""
        return self.region.platform

    @lazy_property
    def locale(self) -> Platform:
        """The locale for this realm."""
        return self._data[RealmData].locale

    @CassiopeiaGhost.property(RealmData)
    @ghost_load_on
    def version(self) -> str:
        return self._data[RealmData].version

    @CassiopeiaGhost.property(RealmData)
    @ghost_load_on
    def language(self) -> str:
        """Default language for this realm."""
        return self._data[RealmData].language

    @CassiopeiaGhost.property(RealmData)
    @ghost_load_on
    def latest_versions(self) -> Dict[str, str]:
        """Latest changed version for each data type listed."""
        return self._data[RealmData].latestVersions

    @CassiopeiaGhost.property(RealmData)
    @ghost_load_on
    def legacy_mode(self) -> str:
        return self._data[RealmData].legacyMode

    @CassiopeiaGhost.property(RealmData)
    @ghost_load_on
    def latest_data_dragon(self) -> str:
        return self._data[RealmData].latestDataDragon

    @CassiopeiaGhost.property(RealmData)
    @ghost_load_on
    def language(self) -> str:
        return self._data[RealmData].language

    @CassiopeiaGhost.property(RealmData)
    @ghost_load_on
    def max_profile_icon_id(self) -> int:
        return self._data[RealmData].maxProfileIconId

    @CassiopeiaGhost.property(RealmData)
    @ghost_load_on
    def store(self) -> str:
        return self._data[RealmData].store

    @CassiopeiaGhost.property(RealmData)
    @ghost_load_on
    def cdn(self) -> str:
        return self._data[RealmData].cdn

    @CassiopeiaGhost.property(RealmData)
    @ghost_load_on
    def css_version(self) -> str:
        return self._data[RealmData].css_version
