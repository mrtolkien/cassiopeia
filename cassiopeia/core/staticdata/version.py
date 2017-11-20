from typing import Union

from merakicommons.cache import lazy_property

from ...data import Region, Platform
from ...dto.staticdata.version import VersionListDto
from ..common import CoreDataList, CassiopeiaList, provide_default_region


class VersionListData(CoreDataList):
    _dto_type = VersionListDto
    _renamed = {}


class Versions(CassiopeiaList):
    _data_types = {VersionListData}

    @provide_default_region
    def __init__(self, *args, region: Union[Region, str] = None):
        kwargs = {"region": region}
        super().__init__(*args, **kwargs)

    @lazy_property
    def region(self) -> Region:
        return Region(self._data[VersionListData].region)

    @lazy_property
    def platform(self) -> Platform:
        return self.region.platform
