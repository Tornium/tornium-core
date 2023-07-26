# Copyright (C) 2021-2023 tiksan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import time

from flask_login import current_user
from mongoengine.queryset.visitor import Q
from tornium_celery.tasks.api import tornget
from tornium_commons.errors import MissingKeyError
from tornium_commons.models import FactionModel, PositionModel, UserModel


class Faction:
    def __init__(self, tid):
        """
        Retrieves the faction from the database.

        :param tid: Torn faction ID
        :param key: Torn API Key to be utilized (uses current user's key if not passed)
        """

        faction = FactionModel.objects(tid=tid).first()
        if faction is None:
            raise ValueError("Unknown Faction")

        self.tid = tid
        self.name = faction.name
        self.respect = faction.respect
        self.capacity = faction.capacity
        self.leader = faction.leader
        self.coleader = faction.coleader
        self.aa_keys = faction.aa_keys

        self.last_members = faction.last_members
        self.last_attacks = faction.last_attacks

        self.guild = faction.guild
        self.config = faction.config

        self.stat_config = faction.statconfig

        self.od_channel = faction.od_channel
        self.chain_od = faction.chainod

    def refresh(self, key=None, force=False):
        now = int(time.time())

        if force or (now - self.last_members) > 1800:
            if key is None:
                key = current_user.key

                if key == "":
                    raise MissingKeyError

            faction_data = tornget(f"faction/{self.tid}?selections=basic", key=key)

            faction: FactionModel = FactionModel.objects(tid=self.tid).first()
            faction.name = faction_data["name"]
            faction.respect = faction_data["respect"]
            faction.capacity = faction_data["capacity"]
            faction.leader = faction_data["leader"]
            faction.coleader = faction_data["co-leader"]
            faction.last_members = now
            faction.save()

            for member_id, member_data in faction_data["members"].items():
                if member_data["position"] == "Recruit":
                    position_pid = None
                    faction_aa = False
                elif member_data["position"] in ("Leader", "Co-leader"):
                    position_pid = None
                    faction_aa = True
                else:
                    position: PositionModel = PositionModel.objects(
                        Q(name=member_data["position"]) & Q(factiontid=faction_data["ID"])
                    ).first()

                    if position is None:
                        position_pid = None
                        faction_aa = False
                    else:
                        position_pid = position.pid
                        faction_aa = position.canAccessFactionApi

                UserModel.objects(tid=int(member_id)).modify(
                    upsert=True,
                    new=True,
                    set__name=member_data["name"],
                    set__level=member_data["level"],
                    set__last_action=member_data["last_action"]["timestamp"],
                    set__status=member_data["last_action"]["status"],
                    set__factionid=faction_data["ID"],
                    set__faction_position=position_pid,
                    set__factionaa=faction_aa,
                )

    def get_bankers(self):
        banker_positions = PositionModel.objects(
            Q(factiontid=self.tid) & (Q(canGiveMoney=True) | Q(canGivePoints=True) | Q(canAdjustMemberBalance=True))
        )
        bankers = []

        banker_position: PositionModel
        for banker_position in banker_positions:
            users = UserModel.objects(faction_position=banker_position.pid).only("tid")

            user: UserModel
            for user in users:
                bankers.append(user.tid)

        if self.leader != 0:
            bankers.append(self.leader)
        if self.coleader != 0:
            bankers.append(self.coleader)

        return bankers
