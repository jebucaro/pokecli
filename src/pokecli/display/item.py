from rich.console import Console
from rich.panel import Panel

from pokecli.display.common import format_name, get_chars, panel_title
from pokecli.models.item import Item


def render_item(item: Item, console: Console) -> None:
    chars = get_chars(console)

    header = panel_title(item.id, format_name(item.name))
    fling = (
        f"   [bold]Fling Power:[/bold] {item.fling_power}" if item.fling_power else ""
    )
    price = item.representative_purchase_price()
    price_text = f"{chars.currency}{price}" if price is not None else chars.dash
    info = (
        f"[bold]Price:[/bold] {price_text}   "
        f"[bold]Category:[/bold] {item.category.name}"
        f"{fling}\n"
    )
    console.print(Panel(header, expand=False))
    console.print(info)

    if item.prices:
        console.print("[bold]Prices by version group:[/bold]")
        for p in item.prices:
            buy = f"{chars.currency}{p.purchase_price}" if p.purchase_price is not None else chars.dash
            sell = f"{chars.currency}{p.sell_price}" if p.sell_price is not None else chars.dash
            console.print(
                f"  [dim]{p.version_group.name}[/dim] "
                f"({p.currency.name}): buy {buy}, sell {sell}"
            )
        console.print("")

    english_effects = [e for e in item.effect_entries if e.language.name == "en"]
    if english_effects:
        console.print(f"[bold]Effect:[/bold] {english_effects[0].short_effect}\n")

    english_flavor = [f for f in item.flavor_text_entries if f.language.name == "en"]
    if english_flavor:
        console.print(
            f'[dim italic]"{english_flavor[0].text}"[/dim italic]\n'
            f"[dim]{chars.dash} {english_flavor[0].version_group.name}[/dim]"
        )

    if not english_effects and not english_flavor:
        console.print("[dim]No English effect or flavor text available.[/dim]")
