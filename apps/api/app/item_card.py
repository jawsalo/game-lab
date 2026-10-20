"""Structured, display-safe Grim Dawn item card models and mapping."""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, Field

DESCRIPTION_TOKEN_RE = re.compile(r"\^([nwo])")
PROPERTY_PREFIXES = ("character", "defensive", "offensive", "skill")


class DescriptionSegment(BaseModel):
    """A plain text segment with a semantic style from the source markup."""

    text: str
    style: Literal["default", "white", "accent"]


class ItemProperty(BaseModel):
    """One numeric gameplay property, retaining its stable source key."""

    key: str
    value: int | float


class ItemConversion(BaseModel):
    """A single damage or stat conversion."""

    input_type: str = Field(alias="from")
    output_type: str = Field(alias="to")
    percentage: int | float


class RecipeIngredient(BaseModel):
    """A crafting ingredient, optionally allowing one of several item IDs."""

    item_ids: list[str] = Field(alias="itemIds")
    quantity: int


class ItemRecipe(BaseModel):
    """Crafting details for a blueprint or formula."""

    output_item_id: str = Field(alias="outputItemId")
    output_quantity: int = Field(alias="outputQuantity")
    crafting_cost: int | None = Field(default=None, alias="craftingCost")
    ingredients: list[RecipeIngredient]


class ItemCard(BaseModel):
    """Stable API representation for displaying a catalog item."""

    id: str
    name: str
    group: str
    category: str
    slot: str | None = None
    rarity: str | None = None
    level_requirement: int | None = Field(default=None, alias="levelRequirement")
    item_level: int | None = Field(default=None, alias="itemLevel")
    bitmap: str | None = None
    description: list[DescriptionSegment] | None = None
    expansions: list[str] = Field(default_factory=list)
    properties: list[ItemProperty] = Field(default_factory=list)
    conversions: list[ItemConversion] = Field(default_factory=list)
    recipe: ItemRecipe | None = None


def _description_segments(value: Any) -> list[DescriptionSegment] | None:
    if not isinstance(value, str) or not value:
        return None

    styles = {"n": "default", "w": "white", "o": "accent"}
    result: list[DescriptionSegment] = []
    current_style = "default"
    cursor = 0

    for match in DESCRIPTION_TOKEN_RE.finditer(value):
        if match.start() > cursor:
            result.append(
                DescriptionSegment(text=value[cursor : match.start()], style=current_style)
            )
        current_style = styles[match.group(1)]
        cursor = match.end()

    if cursor < len(value):
        result.append(DescriptionSegment(text=value[cursor:], style=current_style))

    return result or None


def _numeric_properties(record: dict[str, Any]) -> list[ItemProperty]:
    return [
        ItemProperty(key=key, value=value)
        for key, value in sorted(record.items())
        if key.startswith(PROPERTY_PREFIXES)
        and key not in {"conversionInType", "conversionOutType", "conversionPercentage"}
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
    ]


def _conversion(record: dict[str, Any]) -> list[ItemConversion]:
    input_type = record.get("conversionInType")
    output_type = record.get("conversionOutType")
    percentage = record.get("conversionPercentage")
    if (
        isinstance(input_type, str)
        and isinstance(output_type, str)
        and isinstance(percentage, (int, float))
        and not isinstance(percentage, bool)
    ):
        return [
            ItemConversion(
                **{"from": input_type, "to": output_type, "percentage": percentage}
            )
        ]
    return []


def _ingredient_ids(value: Any) -> list[str]:
    if isinstance(value, str) and value:
        return [value]
    if isinstance(value, list):
        return [item_id for item_id in value if isinstance(item_id, str) and item_id]
    return []


def _recipe(record: dict[str, Any]) -> ItemRecipe | None:
    output_item_id = record.get("artifactName")
    if not isinstance(output_item_id, str) or not output_item_id:
        return None

    ingredients: list[RecipeIngredient] = []
    for key, value in sorted(record.items()):
        match = re.fullmatch(r"reagent(\d+)BaseName", key)
        if match:
            item_ids = _ingredient_ids(value)
            quantity = record.get(f"reagent{match.group(1)}Quantity", 1)
        elif key == "reagentBaseBaseName":
            item_ids = _ingredient_ids(value)
            quantity = record.get("reagentBaseQuantity", 1)
        else:
            continue

        if item_ids and isinstance(quantity, int) and not isinstance(quantity, bool):
            ingredients.append(RecipeIngredient(itemIds=item_ids, quantity=quantity))

    output_quantity = record.get("artifactCreateQuantity", 1)
    crafting_cost = record.get("artifactCreationCost")
    return ItemRecipe(
        outputItemId=output_item_id,
        outputQuantity=output_quantity if isinstance(output_quantity, int) else 1,
        craftingCost=crafting_cost if isinstance(crafting_cost, int) else None,
        ingredients=ingredients,
    )


def build_item_card(item: dict[str, Any]) -> ItemCard:
    """Map a catalog item to a display contract without exposing raw record data."""
    record = item.get("record")
    if not isinstance(record, dict):
        record = {}

    return ItemCard(
        id=item["id"],
        name=item["name"],
        group=item["group"],
        category=item["category"],
        slot=item.get("slot"),
        rarity=item.get("rarity"),
        levelRequirement=item.get("levelRequirement"),
        itemLevel=item.get("itemLevel"),
        bitmap=item.get("bitmap"),
        description=_description_segments(item.get("description")),
        expansions=item.get("mods") or [],
        properties=_numeric_properties(record),
        conversions=_conversion(record),
        recipe=_recipe(record),
    )
