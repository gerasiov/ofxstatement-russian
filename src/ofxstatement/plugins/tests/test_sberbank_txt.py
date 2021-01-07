import datetime

from ofxstatement.ui import UI
from ofxstatement.plugins.sberbank_txt import SberBankTxtPlugin
from .util import file_sample


def test_parse_maestro():
    plugin = SberBankTxtPlugin(UI(), {})
    s = plugin.get_parser(file_sample('sberbank_maestro.txt')).parse()

    assert s is not None

    assert s.account_id == 'СБЕРБАНК - MAESTRO XXXXXXXXX XXXX40696 ОСНОВНАЯ'
    assert s.currency == 'RUR'
    assert s.bank_id == 'SberBank'
    assert s.end_balance == 0
    assert s.start_balance == 0

    assert len(s.lines) == 4

    assert all(l.amount for l in s.lines)

    line0 = s.lines[0]

    assert line0.amount == 10000.0
    assert line0.memo == 'SBOL MOSCOW RUS'
    assert line0.date == datetime.datetime(2019, 3, 26, 0, 0)
    assert line0.trntype == 'DEBIT'


def test_parse_visa():
    plugin = SberBankTxtPlugin(UI(), {})
    s = plugin.get_parser(file_sample('sberbank_visa.txt')).parse()

    assert s is not None

    assert s.account_id == 'VISA GOLD XXXX XXXX XXX4 6122 ОСНОВНАЯ'
    assert s.currency == 'RUR'

    assert s.bank_id == 'SberBank'
    assert s.end_balance == 20877.29
    assert s.start_balance == 318.3

    assert len(s.lines) == 34

    assert all(l.amount for l in s.lines)

    assert s.lines[2].memo == 'ПОПОЛНЕНИЕ СЧЕТА'
    assert s.lines[2].trntype == 'DEBIT'

    assert s.lines[7].memo == 'PEREKRESTOK KRYLATSKOY E NOGINSK RU'
    assert s.lines[7].trntype == 'CREDIT'
    assert s.lines[7].amount == -1699.0
    assert s.lines[7].date == datetime.datetime(2018, 10, 4, 0, 0)

    assert s.lines[14].memo == 'TINKOFF BANK CARD2CARD Visa Direct RU'

    assert s.lines[25].memo == 'Rocketbank.ru Card2Car d MOSCOW RU'
    assert s.lines[25].trntype == 'CREDIT'

    assert abs(sum(l.amount for l in s.lines) + s.start_balance - s.end_balance) < 0.001
