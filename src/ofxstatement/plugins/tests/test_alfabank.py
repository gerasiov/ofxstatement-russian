import datetime
from decimal import Decimal
from unittest import mock

from ofxstatement.plugins.alfabank import AlfabankPlugin
from .util import file_sample


def test_parser():
    plugin = AlfabankPlugin(mock.Mock(), {'user_date': 'false'})
    statement = plugin.get_parser(file_sample("alfabank.csv")).parse()
    assert statement.bank_id == 'Alfabank'
    assert statement.currency == 'RUR'
    assert statement.account_id == '11111111111111111111'

    _check_line(statement.lines[0], '33123.56', datetime.datetime(2017, 5, 31, 0, 0),
                '{VO11111} Перечисление ден. средств (зарплата за май 2017 г.)', 'ABCDEF11111111111', 'DEBIT')
    _check_line(statement.lines[1], '-50', datetime.datetime(2017, 5, 3, 0, 0),
                'Комиссия за переводы в рублях за период с1МАЙ17 по 1МАЙ17 поруч.поданы ч/з '
                'ИнтернетБанк Согл.тариф.Банка Иванов Иван Иванович', 'ABCDEF22222222222', 'SRVCHG')
    _check_line(statement.lines[2], '-1500', datetime.datetime(2017, 5, 3, 0, 0),
                '123456++++++6789    11111111\\123\\Visa Direct\\SOME BANK             '
                '03.05.17 01.05.17    1500.00  RUR MCC1234', 'ABC_1AA11A', 'CREDIT')


def test_user_date():
    plugin = AlfabankPlugin(mock.Mock(), {})
    statement = plugin.get_parser(file_sample("alfabank.csv")).parse()

    assert statement.lines[2].date == datetime.datetime(2017, 5, 1, 0, 0)


def _check_line(line, amount, date, memo, refnum, trntype):
    assert line.amount == Decimal(amount)
    assert line.date == date
    assert line.memo == memo
    assert line.refnum == refnum
    assert line.trntype == trntype
