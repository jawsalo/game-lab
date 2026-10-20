"""HTTP routes for the Grim Dawn item catalog."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query

from .catalog import CatalogUnavailableError, GrimDawnCatalog
from .item_card import ItemCard, build_item_card

router = APIRouter(prefix="/api/grim-dawn", tags=["grim-dawn"])
catalog = GrimDawnCatalog()


def unavailable(error: CatalogUnavailableError) -> HTTPException:
    return HTTPException(status_code=503, detail=str(error))


@router.get("/catalog")
def catalog_metadata() -> dict[str, Any]:
    """Return catalog version, record count, and filter facets."""
    try:
        return catalog.metadata()
    except CatalogUnavailableError as error:
        raise unavailable(error) from error


@router.get("/items")
def search_items(
    q: Annotated[str | None, Query(max_length=200)] = None,
    item_group: Annotated[
        str | None,
        Query(alias="group", max_length=50),
    ] = None,
    category: Annotated[str | None, Query(max_length=100)] = None,
    slot: Annotated[str | None, Query(max_length=50)] = None,
    rarity: Annotated[str | None, Query(max_length=50)] = None,
    level_min: Annotated[int | None, Query(alias="levelMin", ge=0)] = None,
    level_max: Annotated[int | None, Query(alias="levelMax", ge=0)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    """Search and filter catalog records."""
    if (
        level_min is not None
        and level_max is not None
        and level_min > level_max
    ):
        raise HTTPException(
            status_code=400,
            detail="levelMin cannot be greater than levelMax",
        )

    try:
        return catalog.search_items(
            query=q,
            item_group=item_group,
            category=category,
            slot=slot,
            rarity=rarity,
            level_min=level_min,
            level_max=level_max,
            limit=limit,
            offset=offset,
        )
    except CatalogUnavailableError as error:
        raise unavailable(error) from error


@router.get("/items/{item_id}")
def get_item(item_id: str) -> dict[str, Any]:
    """Return one catalog record by its stable GrimTools item ID."""
    try:
        item = catalog.get_item(item_id)
    except CatalogUnavailableError as error:
        raise unavailable(error) from error

    if item is None:
        raise HTTPException(status_code=404, detail="item not found")
    return item


@router.get(
    "/items/{item_id}/card",
    response_model=ItemCard,
    response_model_exclude_none=True,
)
def get_item_card(item_id: str) -> ItemCard:
    """Return a structured, display-safe card for one catalog item."""
    try:
        item = catalog.get_item(item_id)
    except CatalogUnavailableError as error:
        raise unavailable(error) from error

    if item is None:
        raise HTTPException(status_code=404, detail="item not found")
    return build_item_card(item)
