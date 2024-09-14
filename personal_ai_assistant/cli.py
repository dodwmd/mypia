import click
from rich.console import Console

console = Console()

@click.group()
def cli():
    """Personal AI Assistant CLI"""
    pass

@cli.command()
def hello():
    """Say hello to the AI assistant"""
    console.print("[bold green]Hello from your Personal AI Assistant![/bold green]")

if __name__ == "__main__":
    cli()
