# -*- coding: utf-8 -*-

"""
Console script for investing.

Use exported unrealized gains / losses csv as input, making sure to first strip
header and footer row if necessary.

"""

import locale
from functools import partial

import click
import pandas as pd


def to_numeric(s):
    return pd.to_numeric(s.str.replace(r'\$', '').str.replace('%', ''))


@click.command()
@click.argument('unrealized', type=click.File('r'))
def main(unrealized):
    """Console script for investing."""
    # Locale formatting init
    locale.setlocale(locale.LC_ALL, 'en_US')
    format_currency = partial(locale.currency, grouping=True)

    # Import csv
    df = pd.read_csv(unrealized)

    # Convert to numeric
    df['gain_loss_abs'] = to_numeric(df['Gain/Loss($)'])
    df['gain_loss_pct'] = to_numeric(df['Gain/Loss(%)'])
    df['market_value'] = to_numeric(df['Market Value'])

    # Format
    df['Market Value'] = df.market_value.apply(format_currency)
    df['Gain/Loss($)'] = df.gain_loss_abs.apply(format_currency)

    # Total holdings
    total = df.market_value.sum()

    # Sell stocks with lowest gain/loss % until we start to accrue a gain
    df.sort_values('gain_loss_pct', inplace=True)
    df['sell'] = df.gain_loss_abs.cumsum() < 0
    groups = df.groupby('sell')
    to_sell = pd.DataFrame(groups.get_group(True))

    # Summarize stocks sold / kept
    results = pd.DataFrame(dict(
        count=groups.market_value.count(),
        sum=groups.market_value.sum().apply(format_currency),
        pct=(100 * groups.market_value.sum() / total).map('{:,.2f}%'.format),
    ), columns=['count', 'sum', 'pct'])

    # Print info
    click.echo('Total money: {}'.format(format_currency(total)))
    click.echo('Total stocks: {}\n'.format(df.market_value.count()))
    click.echo('Sell/keep:\n{}\n'.format(results))
    click.echo('Realized gain/loss: {}\n'.format(
        format_currency(to_sell.gain_loss_abs.sum())
    ))
    click.echo('Stocks to sell:\n{}'.format(
        to_sell[['Symbol', 'Name', 'Market Value', 'Gain/Loss($)']]
    ))

    # Output csv
    del df['gain_loss_abs']
    del df['gain_loss_pct']
    del df['market_value']
    del df['Day Change($)']
    del df['Day Change(%)']
    df.to_csv('stocks.csv', index=False)


if __name__ == "__main__":
    main()
