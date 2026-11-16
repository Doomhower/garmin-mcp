import hashlib
import os
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers
from garmin_personal_api import GarminPersonalApiClient, PersonalApiAuthenticator

mcp = FastMCP("garmin-personal")

# Bearer tokens are cached per API key (by fingerprint) so several clients with
# different keys don't overwrite each other's cache. The key itself is never
# written to disk.
TOKEN_CACHE_DIR = Path(os.environ.get("GARMIN_TOKEN_CACHE_DIR", "/tmp/garmin-mcp-tokens"))

API_KEY_HEADER = "x-garmin-api-key"


def _api_key_from_request() -> str:
    """Read the Garmin personal API key sent by the MCP client.

    Accepted, in this order:
      X-Garmin-Api-Key: <key>
      Authorization: Bearer <key>
    """
    headers = get_http_headers(include={"authorization"})
    key = headers.get(API_KEY_HEADER, "").strip()
    if not key:
        auth = headers.get("authorization", "").strip()
        scheme, _, value = auth.partition(" ")
        if scheme.lower() in ("bearer", "apikey"):
            key = value.strip()
    if not key:
        raise ToolError(
            "No Garmin API key provided. Configure your MCP client to send it in the "
            "'X-Garmin-Api-Key' header (or 'Authorization: Bearer <key>')."
        )
    return key


def get_client() -> GarminPersonalApiClient:
    """Fresh client for the calling MCP client's API key. The bearer token is
    cached and only re-fetched when nearly expired (tokens live 24h)."""
    key = _api_key_from_request()
    fingerprint = hashlib.sha256(key.encode()).hexdigest()[:32]
    TOKEN_CACHE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    cache_file = TOKEN_CACHE_DIR / f"{fingerprint}.json"
    with PersonalApiAuthenticator(bearer_token_cache_file=cache_file) as auth:
        token = auth.obtain_token(key)
    return GarminPersonalApiClient(token.access_token)


def _as_object(data: Any) -> dict:
    """Garmin returns either an object or a list depending on the endpoint.
    MCP structured output must be an object, so lists are wrapped. Wrapping
    also keeps empty results visible instead of an empty response."""
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return {"count": len(data), "items": data}
    return {"result": data}


@mcp.tool()
def sleep(d: str) -> dict:
    """Detailed sleep for one day (YYYY-MM-DD): stages, durations, interruptions."""
    with get_client() as c:
        return _as_object(c.get_daily_sleep(d))


@mcp.tool()
def sleep_summaries(start: str, end: str) -> dict:
    """Per-day sleep summaries/scores across a date range (YYYY-MM-DD)."""
    with get_client() as c:
        return _as_object(c.get_daily_sleep_summaries(start, end))


@mcp.tool()
def steps(start: str, end: str) -> dict:
    """Daily step counts for a date range."""
    with get_client() as c:
        return _as_object(c.get_daily_steps(start, end))


@mcp.tool()
def heart_rate(d: str) -> dict:
    """Daily heart rate (resting/avg/min/max) for one day."""
    with get_client() as c:
        return _as_object(c.get_daily_heart_rate(d))


@mcp.tool()
def hrv(d: str) -> dict:
    """HRV for one day."""
    with get_client() as c:
        return _as_object(c.get_daily_hrv(d))


@mcp.tool()
def spo2(d: str) -> dict:
    """Nightly SpO2/acclimation for one day."""
    with get_client() as c:
        return _as_object(c.get_daily_spo2(d))


@mcp.tool()
def body_battery(start: str, end: str) -> dict:
    """Body Battery daily reports for a date range."""
    with get_client() as c:
        return _as_object(c.get_daily_body_battery(start, end))


@mcp.tool()
def stress(start: str, end: str) -> dict:
    """Daily stress for a date range."""
    with get_client() as c:
        return _as_object(c.get_daily_stress(start, end))


@mcp.tool()
def hydration(start: str, end: str) -> dict:
    """Daily hydration for a date range."""
    with get_client() as c:
        return _as_object(c.get_daily_hydration(start, end))


@mcp.tool()
def weight(start: str, end: str) -> dict:
    """All weight measurements in a date range."""
    with get_client() as c:
        return _as_object(c.get_weight_measurements(start, end))


@mcp.tool()
def daily_summaries(start: str, end: str) -> dict:
    """Combined daily summary (steps, calories, sleep, ...) for a range."""
    with get_client() as c:
        return _as_object(c.get_daily_summaries(start, end))


@mcp.tool()
def activities(limit: int = 10, offset: int = 0) -> dict:
    """Recent workouts/activities, newest first."""
    with get_client() as c:
        return _as_object(c.search_activities(start=offset, limit=limit))


@mcp.tool()
def activity(activity_id: int) -> dict:
    """Full details for one activity (distance, pace splits, HR, ...)."""
    with get_client() as c:
        return _as_object(c.get_activity(activity_id))


def main() -> None:
    mcp.run(transport="http", host="0.0.0.0", port=8091)


if __name__ == "__main__":
    main()
