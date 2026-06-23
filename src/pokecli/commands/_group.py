import typer
from typer.core import TyperGroup


class ResourceGroup(TyperGroup):
    """Allow `pokecli pokemon pikachu` as a shortcut for `pokecli pokemon get pikachu`."""

    def resolve_command(self, ctx: typer.Context, args: list[str]):
        if args:
            first = args[0]
            if not first.startswith("-") and first not in self.commands:
                args = ["get", *args]
        return super().resolve_command(ctx, args)
