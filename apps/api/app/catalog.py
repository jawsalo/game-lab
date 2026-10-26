"""Read-only access to the pinned Grim Dawn item catalog."""

from __future__ import annotations

import json
import os
import re
import sqlite3
from collections.abc import Sequence
from pathlib import Path
from typing import Any

DEFAULT_DATABASE_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "grim-dawn"
    / "1.3.1.0"
    / "items.sqlite"
)
DATABASE_ENVIRONMENT_VARIABLE = "GRIM_DAWN_DATABASE_PATH"
SEARCH_TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)

ITEM_STYLE_NAME_PREFIXES = {
    "tagStyleUniqueTier2": "Empowered",
    "tagStyleUniqueTier3": "Mythical",
}


class CatalogUnavailableError(RuntimeError):
    """Raised when the pinned catalog cannot be opened or queried."""


def catalog_database_path() -> Path:
    """Return the configured catalog path, or the packaged database path."""
    configured = os.getenv(DATABASE_ENVIRONMENT_VARIABLE)
    return Path(configured) if configured else DEFAULT_DATABASE_PATH


def _fts_query(value: str) -> str | None:
    tokens = SEARCH_TOKEN_RE.findall(value.casefold())
    if not tokens:
        return None
    return " AND ".join(f'"{token}"*' for token in tokens)


def _execute(
    connection: sqlite3.Connection,
    statement: str,
    parameters: Sequence[Any] = (),
) -> sqlite3.Cursor:
    """Execute through an explicit cursor so SQLite instrumentation can trace it."""
    cursor = connection.cursor()
    cursor.execute(statement, parameters)
    return cursor


def _display_name(name: str | None, record: dict[str, Any]) -> str | None:
    """Restore localized item-tier prefixes retained in the raw record."""
    style_tag = record.get("itemStyleTag")
    prefix = (
        ITEM_STYLE_NAME_PREFIXES.get(style_tag)
        if isinstance(style_tag, str)
        else None
    )
    if not name or not prefix or name.casefold().startswith(f"{prefix.casefold()} "):
        return name
    return f"{prefix} {name}"


def _item_summary(row: sqlite3.Row) -> dict[str, Any]:
    record = json.loads(row["record_json"])
    return {
        "id": row["id"],
        "name": _display_name(row["name"], record),
        "description": row["description"],
        "group": row["item_group"],
        "category": row["category"],
        "slot": row["slot"],
        "rarity": row["rarity"],
        "levelRequirement": row["level_requirement"],
        "itemLevel": row["item_level"],
        "bitmap": row["bitmap"],
        "mods": json.loads(row["mods_json"]),
    }


class GrimDawnCatalog:
    """Query a versioned Grim Dawn SQLite catalog without mutating it."""

    def __init__(self, database_path: Path | None = None) -> None:
        self.database_path = database_path or catalog_database_path()

    def connect(self) -> sqlite3.Connection:
        if not self.database_path.is_file():
            raise CatalogUnavailableError(
                f"catalog database not found: {self.database_path}"
            )

        uri = f"{self.database_path.resolve().as_uri()}?mode=ro&immutable=1"
        try:
            connection = sqlite3.connect(uri, uri=True)
            connection.row_factory = sqlite3.Row
            _execute(connection, "PRAGMA query_only = ON")
            return connection
        except sqlite3.Error as error:
            raise CatalogUnavailableError(
                f"cannot open catalog database: {error}"
            ) from error

    def readiness(self) -> dict[str, Any]:
        """Verify that the expected catalog is available for requests."""
        try:
            with self.connect() as connection:
                application_id = _execute(connection, 
                    "PRAGMA application_id"
                ).fetchone()[0]
                metadata = dict(
                    _execute(connection, 
                        """
                        SELECT key, value
                        FROM metadata
                        WHERE key IN ('game_version', 'record_count')
                        """
                    )
                )
                item_count = _execute(connection, 
                    "SELECT COUNT(*) FROM items"
                ).fetchone()[0]
        except sqlite3.Error as error:
            raise CatalogUnavailableError(
                f"catalog readiness check failed: {error}"
            ) from error

        record_count = int(metadata.get("record_count", "-1"))
        game_version = metadata.get("game_version")
        if application_id != 0x47444C42:
            raise CatalogUnavailableError("catalog application ID is invalid")
        if not game_version or item_count != record_count:
            raise CatalogUnavailableError("catalog metadata or row count is invalid")

        return {
            "gameVersion": game_version,
            "recordCount": record_count,
        }

    def metadata(self) -> dict[str, Any]:
        try:
            with self.connect() as connection:
                metadata = dict(
                    _execute(connection, 
                        "SELECT key, value FROM metadata ORDER BY key"
                    )
                )
                groups = dict(
                    _execute(connection, 
                        """
                        SELECT item_group, COUNT(*)
                        FROM items
                        GROUP BY item_group
                        ORDER BY item_group
                        """
                    )
                )
                categories = dict(
                    _execute(connection, 
                        """
                        SELECT category, COUNT(*)
                        FROM items
                        GROUP BY category
                        ORDER BY category
                        """
                    )
                )
        except sqlite3.Error as error:
            raise CatalogUnavailableError(f"cannot read catalog metadata: {error}") from error

        return {
            "gameVersion": metadata["game_version"],
            "schemaVersion": int(metadata["schema_version"]),
            "recordCount": int(metadata["record_count"]),
            "groups": groups,
            "categories": categories,
        }

    def get_item(self, item_id: str) -> dict[str, Any] | None:
        try:
            with self.connect() as connection:
                row = _execute(connection, 
                    """
                    SELECT
                        id, name, description, item_group, category, slot,
                        rarity, level_requirement, item_level, bitmap, mods_json,
                        name_tag, name_source, name_source_item_id,
                        description_tag, category_code, record_json
                    FROM items
                    WHERE id = ?
                    """,
                    (item_id,),
                ).fetchone()
        except sqlite3.Error as error:
            raise CatalogUnavailableError(f"cannot read catalog item: {error}") from error

        if row is None:
            return None

        item = _item_summary(row)
        item.update(
            {
                "nameTag": row["name_tag"],
                "nameSource": row["name_source"],
                "nameSourceItemId": row["name_source_item_id"],
                "descriptionTag": row["description_tag"],
                "categoryCode": row["category_code"],
                "record": json.loads(row["record_json"]),
            }
        )
        return item

    def search_items(
        self,
        *,
        query: str | None = None,
        item_group: str | None = None,
        category: str | None = None,
        slot: str | None = None,
        rarity: str | None = None,
        level_min: int | None = None,
        level_max: int | None = None,
        highest_level_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        clauses: list[str] = []
        parameters: list[Any] = []
        join = ""
        fts_query = _fts_query(query or "")

        if query and fts_query is None:
            return {"items": [], "total": 0, "limit": limit, "offset": offset}
        if fts_query:
            join = "JOIN items_fts ON items_fts.id = items.id"
            clauses.append("items_fts MATCH ?")
            parameters.append(fts_query)

        filters = (
            ("items.item_group", item_group),
            ("items.category", category),
            ("items.slot", slot),
            ("items.rarity", rarity),
        )
        for column, value in filters:
            if value:
                clauses.append(f"{column} = ?")
                parameters.append(value)

        if level_min is not None:
            clauses.append("items.level_requirement >= ?")
            parameters.append(level_min)
        if level_max is not None:
            clauses.append("items.level_requirement <= ?")
            parameters.append(level_max)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        from_sql = f"FROM items {join} {where}"
        if highest_level_only:
            family_name = """
                CASE
                    WHEN items.name_sort LIKE 'mythical %'
                        THEN substr(items.name_sort, 10)
                    WHEN items.name_sort LIKE 'empowered %'
                        THEN substr(items.name_sort, 11)
                    WHEN items.name_sort LIKE 'elite %'
                        THEN substr(items.name_sort, 7)
                    ELSE items.name_sort
                END
            """
            from_sql = f"""
                FROM (
                    SELECT *
                    FROM (
                        SELECT
                            items.*,
                            ROW_NUMBER() OVER (
                                PARTITION BY
                                    items.item_group,
                                    items.category,
                                    COALESCE(items.slot, ''),
                                    {family_name}
                                ORDER BY
                                    COALESCE(
                                        items.level_requirement,
                                        items.item_level,
                                        0
                                    ) DESC,
                                    items.item_level DESC,
                                    items.id
                            ) AS version_rank
                        FROM items {join} {where}
                    ) AS ranked_items
                    WHERE version_rank = 1
                ) AS items
            """
        order_sql = "items.name_sort, items.id"
        order_parameters: list[Any] = []
        if query and fts_query:
            normalized_query = query.strip().casefold()
            order_sql = (
                "CASE "
                "WHEN items.name_sort = ? THEN 0 "
                "WHEN items.name_sort LIKE ? THEN 1 "
                "ELSE 2 END, items.name_sort, items.id"
            )
            order_parameters = [normalized_query, f"{normalized_query}%"]

        try:
            with self.connect() as connection:
                total = _execute(connection, 
                    f"SELECT COUNT(*) {from_sql}",
                    parameters,
                ).fetchone()[0]
                rows = _execute(connection, 
                    f"""
                    SELECT
                        items.id, items.name, items.description,
                        items.item_group, items.category, items.slot,
                        items.rarity, items.level_requirement,
                        items.item_level, items.bitmap, items.mods_json,
                        items.record_json
                    {from_sql}
                    ORDER BY {order_sql}
                    LIMIT ? OFFSET ?
                    """,
                    [*parameters, *order_parameters, limit, offset],
                ).fetchall()
        except sqlite3.Error as error:
            raise CatalogUnavailableError(f"cannot search catalog: {error}") from error

        return {
            "items": [_item_summary(row) for row in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
