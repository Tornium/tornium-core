# Copyright (C) tiksan - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by tiksan <webmaster@deek.sh>

import json
import random

from controllers.api.decorators import *
from controllers.api.utils import api_ratelimit_response, make_exception_response
from models.faction import Faction
from models.servermodel import ServerModel
from models.user import User


def jsonified_verify_config(guild: ServerModel):
    return jsonify(
        {
            "enabled": guild.config.get("verify"),
            "verify_template": guild.verify_template,
            "verified_roles": guild.verified_roles,
            "faction_verify": guild.faction_verify,
            "verify_log_channel": guild.verify_log_channel,
        }
    )


@key_required
@ratelimit
@requires_scopes(scopes={"admin", "bot:admin"})
def verification_config(guildid, *args, **kwargs):
    key = f"tornium:ratelimit:{kwargs['user'].tid}"

    guild: ServerModel = ServerModel.objects(sid=guildid).first()

    if guild is None:
        return make_exception_response("1001", key)

    for factiontid, faction_data in guild.faction_verify.items():
        if "positions" not in guild.faction_verify[factiontid]:
            guild.faction_verify[factiontid]["positions"] = {}

    guild.save()

    return (jsonified_verify_config(guild), 200, api_ratelimit_response(key))


@key_required
@ratelimit
@requires_scopes(scopes={"admin", "bot:admin"})
def guild_verification(*args, **kwargs):
    data = json.loads(request.get_data().decode("utf-8"))
    key = f"tornium:ratelimit:{kwargs['user'].tid}"

    guildid = data.get("guildid")

    if guildid in ("", None, 0) or not guildid.isdigit():
        return make_exception_response("1001", key)

    guildid = int(guildid)
    guild: ServerModel = ServerModel.objects(sid=guildid).first()

    if guild is None:
        return make_exception_response("1001", key)

    if request.method == "POST":
        if guild.config.get("verify") in (None, 0):
            guild.config["verify"] = 1
            guild.save()
        else:
            return make_exception_response(
                "0000",
                key,
                details={
                    "message": "Setting already enabled.",
                    "setting": "guild.config.verify",
                },
            )
    elif request.method == "DELETE":
        if guild.config.get("verify") in (None, 1):
            guild.config["verify"] = 0
            guild.save()
        else:
            return make_exception_response(
                "0000",
                key,
                details={
                    "message": "Setting already disabled.",
                    "setting": "guild.config.verify",
                },
            )

    return (jsonified_verify_config(guild), 200, api_ratelimit_response(key))


@key_required
@ratelimit
@requires_scopes(scopes={"admin", "bot:admin"})
def guild_verification_log(*args, **kwargs):
    data = json.loads(request.get_data().decode("utf-8"))
    key = f"tornium:ratelimit:{kwargs['user'].tid}"

    guildid = data.get("guildid")
    channelid = data.get("channel")

    if guildid in ("", None, 0) or not guildid.isdigit():
        return make_exception_response("1001", key)
    elif channelid in ("", None, 0) or not channelid.isdigit():
        return make_exception_response("1002", key)

    guildid = int(guildid)
    channelid = int(channelid)
    guild: ServerModel = ServerModel.objects(sid=guildid).first()

    if guild is None:
        return make_exception_response("1001", key)

    guild.verify_log_channel = channelid
    guild.save()

    return jsonified_verify_config(guild), 200, api_ratelimit_response(key)


@key_required
@ratelimit
@requires_scopes(scopes={"admin", "bot:admin"})
def faction_verification(*args, **kwargs):
    data = json.loads(request.get_data().decode("utf-8"))
    key = f'tornium:ratelimit:{kwargs["user"].tid}'

    guildid = data.get("guildid")
    factiontid = data.get("factiontid")

    if guildid in ("", None, 0) or not guildid.isdigit():
        return make_exception_response("1001", key)
    elif factiontid in ("", None, 0) or not factiontid.isdigit():
        return make_exception_response("1102", key)

    guildid = int(guildid)
    factiontid = int(factiontid)
    guild: ServerModel = ServerModel.objects(sid=guildid).first()

    if guild is None:
        return make_exception_response("1001", key)

    faction: Faction = Faction(factiontid, key=User(random.choice(guild.admins)).key)

    if request.method == "DELETE" and str(faction.tid) not in guild.faction_verify:
        return make_exception_response(
            "0000",
            key,
            details={
                "message": "Faction not in guild's list of factions to verify.",
                "factiontid": factiontid,
            },
        )

    if request.method == "DELETE" and data.get("remove") is True:
        del guild.faction_verify[str(factiontid)]
    else:
        if faction.tid not in guild.faction_verify:
            guild.faction_verify[str(factiontid)] = {
                "roles": [],
                "positions": {},
                "enabled": False,
            }

        if request.method == "POST":
            guild.faction_verify[str(factiontid)]["enabled"] = True
        elif request.method == "DELETE":
            guild.faction_verify[str(factiontid)]["enabled"] = False

    guild.save()

    return (jsonified_verify_config(guild), 200, api_ratelimit_response(key))


@key_required
@ratelimit
@requires_scopes(scopes={"admin", "bot:admin"})
def guild_verification_roles(*args, **kwargs):
    data = json.loads(request.get_data().decode("utf-8"))
    key = f"tornium:ratelimit:{kwargs['user'].tid}"

    guildid = data.get("guildid")
    roles = data.get("roles")

    if guildid in ("", None, 0) or not guildid.isdigit():
        return make_exception_response("1001", key)
    elif roles is None or type(roles) != list:
        return make_exception_response("1000", key)

    guildid = int(guildid)
    guild: ServerModel = ServerModel.objects(sid=guildid).first()

    if guild is None:
        return make_exception_response("1001", key)

    try:
        guild.verified_roles = [int(role) for role in roles]
    except ValueError:
        return make_exception_response("1003", key)

    guild.save()

    return (jsonified_verify_config(guild), 200, api_ratelimit_response(key))


@key_required
@ratelimit
@requires_scopes(scopes={"admin", "bot:admin"})
def faction_roles(factiontid, *args, **kwargs):
    data = json.loads(request.get_data().decode("utf-8"))
    key = f"tornium:ratelimit:{kwargs['user'].tid}"

    guildid = data.get("guildid")
    roles = data.get("roles")

    if guildid in ("", None, 0) or not guildid.isdigit():
        return make_exception_response("1001", key)
    elif roles is None or type(roles) != list:
        return make_exception_response("1000", key)

    guildid = int(guildid)
    guild: ServerModel = ServerModel.objects(sid=guildid).first()

    if guild is None:
        return make_exception_response("1001", key)
    elif str(factiontid) not in guild.faction_verify.keys():
        return make_exception_response("1102", key)

    guild.faction_verify[str(factiontid)]["roles"] = [int(role) for role in roles]
    guild.save()

    return (jsonified_verify_config(guild), 200, api_ratelimit_response(key))


@key_required
@ratelimit
@requires_scopes(scopes={"admin", "bot:admin"})
def faction_position_roles(factiontid: int, position: str, *args, **kwargs):
    data = json.loads(request.get_data().decode("utf-8"))
    key = f"tornium:ratelimit:{kwargs['user'].tid}"

    guildid = data.get("guildid")
    roles = data.get("roles")

    if guildid in ("", None, 0) or not guildid.isdigit():
        return make_exception_response("1001", key)
    elif roles is None or type(roles) != list:
        return make_exception_response("1000", key)

    guildid = int(guildid)
    guild: ServerModel = ServerModel.objects(sid=guildid).first()

    if guild is None:
        return make_exception_response("1001", key)
    elif str(factiontid) not in guild.faction_verify.keys():
        return make_exception_response("1102", key)

    guild.faction_verify[str(factiontid)]["positions"][position] = roles
    guild.save()

    return (jsonified_verify_config(guild), 200, api_ratelimit_response(key))
