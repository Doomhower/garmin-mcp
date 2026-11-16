from fastmcp import FastMCP
from garmin_personal_api import (
    GarminPersonalApiClient,
    PersonalApiAuthenticator,
    resolve_api_key,
)

mcp = FastMCP("garmin-personal")


def get_client() -> GarminPersonalApiClient:
    """Fresh client. The bearer token is cached on disk and only re-fetched
    when nearly expired (tokens live 24h), so this is cheap."""
    with PersonalApiAuthenticator() as auth:
        token = auth.obtain_token(resolve_api_key())
    return GarminPersonalApiClient(token.access_token)


@mcp.tool()
def sleep(d: str) -> dict:
    """Detailed sleep for one day (YYYY-MM-DD): stages, durations, interruptions."""
    with get_client() as c:
        return c.get_daily_sleep(d)


@mcp.tool()
def sleep_summaries(start: str, end: str) -> dict:
    """Per-day sleep summaries/scores across a date range (YYYY-MM-DD)."""
    with get_client() as c:
        return c.get_daily_sleep_summaries(start, end)


@mcp.tool()
def steps(start: str, end: str) -> dict:
    """Daily step counts for a date range."""
    with get_client() as c:
        return c.get_daily_steps(start, end)


@mcp.tool()
def heart_rate(d: str) -> dict:
    """Daily heart rate (resting/avg/min/max) for one day."""
    with get_client() as c:
        return c.get_daily_heart_rate(d)


@mcp.tool()
def hrv(d: str) -> dict:
    """HRV for one day."""
    with get_client() as c:
        return c.get_daily_hrv(d)


@mcp.tool()
def spo2(d: str) -> dict:
    """Nightly SpO2/acclimation for one day."""
    with get_client() as c:
        return c.get_daily_spo2(d)


@mcp.tool()
def body_battery(start: str, end: str) -> dict:
    """Body Battery daily reports for a date range."""
    with get_client() as c:
        return c.get_daily_body_battery(start, end)


@mcp.tool()
def stress(start: str, end: str) -> dict:
    """Daily stress for a date range."""
    with get_client() as c:
        return c.get_daily_stress(start, end)


@mcp.tool()
def hydration(start: str, end: str) -> dict:
    """Daily hydration for a date range."""
    with get_client() as c:
        return c.get_daily_hydration(start, end)


@mcp.tool()
def weight(start: str, end: str) -> dict:
    """All weight measurements in a date range."""
    with get_client() as c:
        return c.get_weight_measurements(start, end)


@mcp.tool()
def daily_summaries(start: str, end: str) -> dict:
    """Combined daily summary (steps, calories, sleep, ...) for a range."""
    with get_client() as c:
        return c.get_daily_summaries(start, end)


@mcp.tool()
def activities(limit: int = 10, offset: int = 0) -> dict:
    """Recent workouts/activities, newest first."""
    with get_client() as c:
        return c.search_activities(start=offset, limit=limit)


@mcp.tool()
def activity(activity_id: int) -> dict:
    """Full details for one activity (distance, pace splits, HR, ...)."""
    with get_client() as c:
        return c.get_activity(activity_id)


def main() -> None:
    mcp.run(transport="http", host="0.0.0.0", port=8091)


if __name__ == "__main__":
    main()
