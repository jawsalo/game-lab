"""Structured, display-safe Grim Dawn item card models and mapping."""

from __future__ import annotations

import math
import re
from typing import Any, Literal

from pydantic import BaseModel, Field

DESCRIPTION_TOKEN_RE = re.compile(r"\^([nwo])")
PROPERTY_PREFIXES = ("character", "defensive", "offensive", "retaliation", "skill")
VARIABLE_PROPERTY_PREFIXES = ("character", "defensive", "offensive", "retaliation")
FIXED_VALUE_PROPERTIES = {
    "characterAttackSpeed",
    "characterConstitution",
    "characterIncreasedExperience",
    "characterIncreasedGold",
    "characterLightRadius",
    "characterManaRegen",
    "characterRunSpeed",
    "characterSpellCastSpeed",
    "characterTotalSpeed",
    "defensiveProtection",
    "offensiveManaBurnDamageRatio",
    "offensiveTauntMin",
}
ZERO_SCALE_PROPERTIES = {
    "offensiveCritDamageModifier",
    "offensiveSlowOffensiveReductionMin",
    "offensiveSlowOffensiveReductionMax",
    "offensiveSlowDefensiveReductionMin",
    "offensiveSlowDefensiveReductionMax",
    "offensiveSlowOffensiveAbilityMin",
    "offensiveSlowOffensiveAbilityMax",
    "offensiveSlowDefensiveAbilityMin",
    "offensiveSlowDefensiveAbilityMax",
    "offensiveLifeLeechMin",
    "offensiveManaBurnDrainMin",
    "offensiveManaBurnDrainMax",
    "skillCooldownReduction",
    "skillCooldownReductionModifier",
    "skillManaCostReduction",
    "skillManaCostReductionModifier",
    "offensiveTotalResistanceReductionPercentMin",
    "offensiveTotalResistanceReductionAbsoluteMin",
    "offensivePhysicalResistanceReductionPercentMin",
    "offensivePhysicalResistanceReductionAbsoluteMin",
    "offensiveElementalResistanceReductionPercentMin",
    "offensiveElementalResistanceReductionAbsoluteMin",
    "offensiveTotalDamageReductionPercentMin",
    "offensiveTotalDamageModifier",
}
FIXED_SUFFIX_RE = re.compile(r"(ReqReduction|DurationMin|DurationMax|Chance|MaxResist|Global|XOR)$")


class DescriptionSegment(BaseModel):
    """A plain text segment with a semantic style from the source markup."""

    text: str
    style: Literal["default", "white", "accent"]


class ItemProperty(BaseModel):
    """One numeric gameplay property, retaining its stable source key."""

    key: str
    value: int | float
    minimum: int | float | None = Field(default=None, alias="minValue")
    maximum: int | float | None = Field(default=None, alias="maxValue")
    duration_seconds: int | float | None = Field(default=None, alias="durationSeconds")


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


def _roll_bounds(
    value: int | float,
    *,
    scale: int | float,
    jitter: int | float,
) -> tuple[int, int]:
    """Calculate the display range used by GrimTools for a variable item stat."""
    lower = min(math.ceil(value * (1 - jitter / 100)), value - 1)
    upper = max(math.floor(value * (1 + jitter / 100)), value + 1)
    multiplier = 1 + scale / 100
    return math.floor(lower * multiplier), math.floor(upper * multiplier)


def _numeric_properties(
    record: dict[str, Any],
    item_group: str | None,
) -> list[ItemProperty]:
    is_equipment = item_group == "equipment"
    scale_value = record.get("h", 0)
    scale = (
        scale_value
        if isinstance(scale_value, (int, float)) and not isinstance(scale_value, bool)
        else 0
    )
    jitter_value = record.get("i", 20)
    jitter = (
        jitter_value
        if isinstance(jitter_value, (int, float)) and not isinstance(jitter_value, bool)
        else 20
    )

    result: list[ItemProperty] = []
    for key, value in sorted(record.items()):
        if (
            not key.startswith(PROPERTY_PREFIXES)
            or key in {"conversionInType", "conversionOutType", "conversionPercentage"}
            or not isinstance(value, (int, float))
            or isinstance(value, bool)
        ):
            continue

        if key == "offensiveSlowPoisonDurationMin":
            continue

        property_data: dict[str, Any] = {"key": key, "value": value}
        is_variable = (
            is_equipment
            and key.startswith(VARIABLE_PROPERTY_PREFIXES)
            and key not in FIXED_VALUE_PROPERTIES
            and not FIXED_SUFFIX_RE.search(key)
        )
        if is_variable:
            property_scale = (
                scale
                if key.startswith("offensive") and key not in ZERO_SCALE_PROPERTIES
                else 0
            )
            minimum, maximum = _roll_bounds(
                value,
                scale=property_scale,
                jitter=jitter,
            )
            if key == "offensiveSlowPoisonMin":
                duration = record.get("offensiveSlowPoisonDurationMin")
                if isinstance(duration, (int, float)) and not isinstance(duration, bool):
                    minimum *= duration
                    maximum *= duration
                    property_data["durationSeconds"] = duration
            property_data["minValue"] = minimum
            property_data["maxValue"] = maximum
        result.append(ItemProperty(**property_data))
    return result


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
        properties=_numeric_properties(record, item.get("group")),
        conversions=_conversion(record),
        recipe=_recipe(record),
    )
