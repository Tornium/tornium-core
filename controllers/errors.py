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

from flask import Blueprint, jsonify, render_template, request
from tornium_commons.errors import DiscordError, NetworkingError, TornError

mod = Blueprint("errors", __name__)


@mod.app_errorhandler(DiscordError)
def discord_error_handler(e: DiscordError):
    return render_template("errors/discord.html", code=e.code, message=e.message), 500


@mod.app_errorhandler(TornError)
def torn_error_handler(e: TornError):
    return render_template("errors/torn.html", code=e.code, message=e.message), 500


@mod.app_errorhandler(NetworkingError)
def networking_error_handler(e: NetworkingError):
    return render_template("errors/networking.html", code=e.code, message=e.message), 500


@mod.app_errorhandler(400)
def error400(e):
    return render_template("errors/400.html"), 400


@mod.app_errorhandler(401)
def error401(e):
    return render_template("errors/401.html"), 401


@mod.app_errorhandler(403)
def error403(e):
    return render_template("errors/403.html"), 403


@mod.app_errorhandler(404)
def error404(e):
    if not request.path.startswith("/api") or request.path in [
        "/api",
        "/api/documentation",
    ]:
        return render_template("errors/404.html"), 404
    else:
        return (
            jsonify(
                {
                    "code": 4010,  # TODO: Update code once determined
                    "name": "EndpointNotFound",
                    "message": "Server failed to find the requested endpoint",
                }
            ),
            404,
        )


@mod.app_errorhandler(500)
def error500(e):
    return render_template("errors/500.html", error=e), 500


@mod.app_errorhandler(501)
def error501(e):
    return render_template("errors/501.html"), 501


@mod.app_errorhandler(503)
def error503(e):
    return render_template("errors/503.html"), 503
