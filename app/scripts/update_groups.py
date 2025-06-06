import asyncio
import os
import requests
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()
DATABASE_URL = os.getenv("APP_CONFIG__DB__URL")
engine = create_async_engine(DATABASE_URL)


def _fetch_raw_groups() -> list[str]:
    response = requests.get(
        "https://edu.sfu-kras.ru/api/timetable/get_insts", verify=False
    )
    response.raise_for_status()
    raw_data = response.json()

    unique_groups = []
    for group in raw_data:
        base_name = group["name"].split(" (")[0] + " (Глобальная группа)"
        if base_name not in unique_groups:
            unique_groups.append(base_name)
        if group["name"] not in unique_groups:
            unique_groups.append(group["name"])
    return unique_groups


async def update_groups():
    groups = _fetch_raw_groups()
    async with engine.begin() as conn:
        for group in groups:
            await conn.execute(
                text(
                    "INSERT INTO groups (name) "
                    "SELECT CAST(:name AS VARCHAR) WHERE NOT EXISTS "
                    "(SELECT 1 FROM groups WHERE name = CAST(:name AS VARCHAR))"
                ),
                {"name": group},
            )


if __name__ == "__main__":
    asyncio.run(update_groups())
