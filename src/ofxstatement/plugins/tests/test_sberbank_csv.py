import os
import datetime

from ofxstatement.ui import UI
from ofxstatement.plugins.sberbank_csv import SberBankCSVPlugin


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')


def test_sberbank():
    plugin = SberBankCSVPlugin(UI(), {'currency': 'RUR'})
    s = plugin.get_parser(os.path.join(SAMPLES_DIR, 'sberbank.csv')).parse()

    assert s is not None

    assert s.account_id == u'Основная *6833'
    assert s.currency == 'RUR'
    assert s.bank_id == 'SberBank'

    assert len(s.lines) == 11

    assert all(l.amount for l in s.lines)

    assert s.lines[0].__dict__ == {
        'amount': -4320.4,
        'check_no': None,
        'date': datetime.datetime(2019, 10, 31, 0, 0),
        'date_user': datetime.datetime(2019, 10, 31, 0, 0),
        'id': None,
        'memo': 'SBOL перевод 4276****1234 И. ИВАН ИВАНОВИЧ, MOSCOW, RUS, 4829',
        'payee': None,
        'refnum': None,
        'trntype': 'CREDIT'
    }

    assert s.lines[3].__dict__ == {
        'amount': 9.01,
        'check_no': None,
        'date': datetime.datetime(2019, 6, 17, 0, 0),
        'date_user': datetime.datetime(2019, 6, 16, 0, 0),
        'id': None,
        'memo': 'SBERBANK ONL@IN VKLAD-KARTA , Moscow, RUS',
        'payee': None,
        'refnum': None,
        'trntype': 'DEBIT'
    }

    assert sum(l.amount for l in s.lines) == 7338.83
