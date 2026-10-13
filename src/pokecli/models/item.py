from pokecli.models.common import BasePokeModel, NamedResource


class ItemEffect(BasePokeModel):
    effect: str
    short_effect: str
    language: NamedResource


class ItemFlavorText(BasePokeModel):
    text: str
    language: NamedResource
    version_group: NamedResource


class ItemPrice(BasePokeModel):
    currency: NamedResource
    # purchase_price/sell_price are null when the item cannot be bought/sold.
    purchase_price: int | None = None
    sell_price: int | None = None
    version_group: NamedResource


class Item(BasePokeModel):
    id: int
    name: str
    # PokeAPI replaced the flat ``cost`` integer with a per-version-group,
    # per-currency ``prices`` list. Default to empty: not every item is priced.
    prices: list[ItemPrice] = []
    fling_power: int | None = None
    category: NamedResource
    effect_entries: list[ItemEffect]
    flavor_text_entries: list[ItemFlavorText]

    def representative_purchase_price(self) -> int | None:
        """A single purchase price for compact views.

        Prefers the poke-dollar entry, then the first entry that has a
        non-null purchase price. Returns ``None`` when nothing is purchasable.
        """
        candidates = [p for p in self.prices if p.purchase_price is not None]
        for price in candidates:
            if price.currency.name == "poke-dollar":
                return price.purchase_price
        return candidates[0].purchase_price if candidates else None
