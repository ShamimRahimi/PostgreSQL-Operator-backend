import click


@click.group()
def cli():
    pass


@cli.command()
def task1():
    from task1 import EndpointTestCases

    EndpointTestCases().run()


if __name__ == "__main__":
    cli()
