import datetime
from typing import Union

from datapipelines import NotFoundError
from merakicommons.cache import lazy, lazy_property
from merakicommons.container import searchable

from ..data import Region, Platform
from .common import CoreData, CassiopeiaObject, CassiopeiaGhost, provide_default_region, ghost_load_on
from .staticdata import ProfileIcon
from ..dto.summoner import SummonerDto


##############
# Data Types #
##############


class AccountData(CoreData):
    _renamed = {"accountId": "id"}


class SummonerData(CoreData):
    _dto_type = SummonerDto
    _renamed = {"summonerLevel": "level"}

    def __call__(self, **kwargs):
        if "accountId" in kwargs:
            self.account = AccountData(id=kwargs.pop("accountId"))
        super().__call__(**kwargs)
        return self


##############
# Core Types #
##############


@searchable({int: ["id"]})
class Account(CassiopeiaObject):
    _data_types = {AccountData}

    @property
    def id(self) -> int:
        return self._data[AccountData].id


@searchable({str: ["name", "region", "platform"], int: ["id", "account"], Region: ["region"], Platform: ["platform"]})
class Summoner(CassiopeiaGhost):
    _data_types = {SummonerData}

    @provide_default_region
    def __init__(self, *, id: int = None, account: Union[Account, int] = None, name: str = None, region: Union[Region, str] = None):
        kwargs = {"region": region}
        if id is not None:
            kwargs["id"] = id
        if name is not None:
            kwargs["name"] = name
        if account and isinstance(account, Account):
            self.__class__.account.fget._lazy_set(self, account)
        elif account is not None:
            kwargs["account_id"] = account
        super().__init__(**kwargs)

    @classmethod
    @provide_default_region
    def __get_query_from_kwargs__(cls, *, id: int = None, account: Union[Account, int] = None, name: str = None, region: Union[Region, str]) -> dict:
        query = {"region": region}
        if id is not None:
            query["id"] = id
        if name is not None:
            query["name"] = name
        if account and isinstance(account, Account):
            query["account.id"] = account.id
        elif account is not None:
            query["account.id"] = account
        return query

    def __get_query__(self):
        query = {"region": self.region, "platform": self.platform}
        try:
            query["id"] = self._data[SummonerData].id
        except AttributeError:
            pass
        try:
            query["account.id"] = self._data[SummonerData].accountId
        except AttributeError:
            pass
        try:
            query["name"] = self._data[SummonerData].name
        except AttributeError:
            pass
        assert "id" in query or "name" in query or "account.id" in query
        return query

    @property
    def exists(self):
        try:
            if not self._Ghost__all_loaded:
                self.__load__()
            self.revision_date  # Make sure we can access this attribute
            return True
        except (AttributeError, NotFoundError):
            return False

    @lazy_property
    def region(self) -> Region:
        """The region for this summoner."""
        return Region(self._data[SummonerData].region)

    @lazy_property
    def platform(self) -> Platform:
        """The platform for this summoner."""
        return self.region.platform

    @CassiopeiaGhost.property(SummonerData)
    @ghost_load_on
    @lazy
    def account(self) -> Account:
        return Account.from_data(self._data[SummonerData].account)

    @CassiopeiaGhost.property(SummonerData)
    @ghost_load_on
    def id(self) -> int:
        return self._data[SummonerData].id

    @CassiopeiaGhost.property(SummonerData)
    @ghost_load_on
    def name(self) -> str:
        return self._data[SummonerData].name

    @CassiopeiaGhost.property(SummonerData)
    @ghost_load_on
    def level(self) -> str:
        return self._data[SummonerData].level

    @CassiopeiaGhost.property(SummonerData)
    @ghost_load_on
    def profile_icon(self) -> ProfileIcon:
        return ProfileIcon(id=self._data[SummonerData].profileIconId, region=self.region)

    @CassiopeiaGhost.property(SummonerData)
    @ghost_load_on
    def revision_date(self) -> datetime.date:
        return datetime.datetime.fromtimestamp(self._data[SummonerData].revisionDate / 1000).date()

    @property
    def match_history_uri(self) -> str:
        return "/v1/stats/player_history/{platform}/{id}".format(platform=self.platform.value, id=self.account.id)

    # Special core methods

    @property
    def champion_masteries(self) -> "ChampionMasteries":
        from .championmastery import ChampionMasteries
        return ChampionMasteries(summoner=self, region=self.region)

    @property
    def match_history(self) -> "MatchHistory":
        from .match import MatchHistory
        return MatchHistory(summoner=self, region=self.region)

    @property
    def current_match(self) -> "CurrentMatch":
        from .spectator import CurrentMatch
        return CurrentMatch(summoner=self, region=self.region)

    @property
    def leagues(self) -> "SummonerLeagues":
        from .league import League, SummonerLeagues
        positions = self.league_positions
        ids = {position.league_id for position in positions}
        return SummonerLeagues([League(id=id_, region=self.region) for id_ in ids])

    @property
    def league_positions(self) -> "LeagueEntries":
        from .league import LeagueEntries
        return LeagueEntries(summoner=self, region=self.region)

    @lazy_property
    def rank_last_season(self):
        most_recent_match = self.match_history[0]
        return most_recent_match.participants[self.name].rankLastSeason
