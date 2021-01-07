import datetime
from decimal import Decimal
from unittest import mock

from ofxstatement.plugins.vtb import VtbPlugin
from .util import file_sample


def test_parser():
    plugin = VtbPlugin(mock.Mock(), {'currency': 'RUR'})
    statement = plugin.get_parser(file_sample("vtb.csv")).parse()
    assert statement.bank_id == 'VTB'
    assert statement.currency == 'RUR'
    assert statement.account_id == '462235******0069'
    assert statement.start_date == datetime.datetime(2019, 7, 7, 0, 0)
    assert statement.end_date == datetime.datetime(2019, 7, 13, 0, 0)
    assert statement.start_balance == Decimal('99955.01')
    assert statement.end_balance == Decimal('82604.01')
    assert len(statement.lines) == 4
    _check_line(statement.lines[0], '-336.15', datetime.datetime(2019, 7, 8, 0, 0), 'Карта *1234 payee1', 'payee1')
    _check_line(statement.lines[1], '-283.48', datetime.datetime(2019, 7, 7, 0, 0), 'Карта *1234 payee2', 'payee2')
    _check_line(statement.lines[2], '-300.00', datetime.datetime(2019, 7, 7, 0, 0), 'Карта *1234 PAY MTS RU TOPUP 1234',
                'PAY MTS RU TOPUP 1234')
    _check_line(statement.lines[3], '-600.00', None, 'Карта *1234 MEGAFON TOPUP  1234', 'MEGAFON TOPUP  1234')


def test_parser_with_user_dates():
    plugin = VtbPlugin(mock.Mock(), {'currency': 'RUR', 'user_date': 'true'})
    parser = plugin.get_parser(file_sample("vtb_user_date.csv"))
    assert parser.user_date
    _check_line(parser.parse().lines[0], '-336.15', datetime.datetime(2019, 7, 6, 0, 0), 'Карта *1234 payee1', 'payee1')


def _check_line(line, amount, date, memo, payee):
    assert line.amount == Decimal(amount)
    assert line.date == date
    assert line.memo == memo
    assert line.payee == payee
