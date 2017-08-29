# -*- coding: utf-8 -*-

"""Console script for investing."""

import locale

import click
import pandas as pd


def to_numeric(s):
    return pd.to_numeric(s.str.replace(r'\$', '').str.replace('%', ''))


@click.command()
@click.option(
    '--unrealized',
    '-u',
    type=click.File('r'),
)
def main(unrealized):
    """Console script for investing."""
    locale.setlocale(locale.LC_ALL, 'en_US')

    df = pd.read_csv(unrealized)

    df['gain_loss_abs'] = to_numeric(df['Gain/Loss($)'])
    df['gain_loss_pct'] = to_numeric(df['Gain/Loss(%)'])
    df['market_value'] = to_numeric(df['Market Value'])

    total = df.market_value.sum()

    df.sort_values('gain_loss_pct', inplace=True)
    df['cumsum'] = df.gain_loss_abs.cumsum(axis=0)
    df['sell'] = df['cumsum'] < 0
    groups = df.groupby('sell')

    results = pd.DataFrame(dict(
        count=groups.market_value.count(),
        sum=groups.market_value.sum(),
        pct=groups.market_value.sum() / total,
    ), columns=['count', 'sum', 'pct'])

    click.echo('Total money: {}'.format(
        locale.currency(total, grouping=True)
    ))
    click.echo('Total stocks: {}'.format(df.market_value.count()))
    click.echo()

    click.echo('Sell/keep:\n{}'.format(results))
    click.echo()

    loss_to_harvest = groups.get_group(True).gain_loss_abs.sum()
    click.echo('Loss left to harvest: {}'.format(
        locale.currency(loss_to_harvest, grouping=True)
    ))
    to_sell = pd.DataFrame(groups.get_group(True))
    click.echo('Stocks to sell:\n{}'.format(
        to_sell[['Symbol', 'Name', 'Market Value', 'Gain/Loss($)']]
    ))


if __name__ == "__main__":
    main()
