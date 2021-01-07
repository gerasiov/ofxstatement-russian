import datetime
from decimal import Decimal

from ofxstatement.ui import UI

from ofxstatement import statement
from ofxstatement.plugins.sberbank_csv import SberBankCSVPlugin
from .util import file_sample


def test_sberbank():
    plugin = SberBankCSVPlugin(UI(), {'currency': 'RUR'})
    s = plugin.get_parser(file_sample('sberbank.csv')).parse()

    assert s is not None

    assert s.account_id == u'Основная *6833'
    assert s.currency == 'RUR'
    assert s.bank_id == 'SberBank'

    assert len(s.lines) == 11

    assert all(l.amount for l in s.lines)

    assert s.lines[0].__dict__ == {
        'amount': Decimal("-4320.4"),
        'check_no': None,
        'date': datetime.datetime(2019, 10, 31, 0, 0),
        'date_user': datetime.datetime(2019, 10, 31, 0, 0),
        'memo': 'SBOL перевод 4276****1234 И. ИВАН ИВАНОВИЧ, MOSCOW, RUS, 4829',
        'payee': None,
        'refnum': None,
        'trntype': 'CREDIT',
        'id': statement.generate_transaction_id(statement.StatementLine(
            date=datetime.datetime(2019, 10, 31, 0, 0),
            memo='SBOL перевод 4276****1234 И. ИВАН ИВАНОВИЧ, MOSCOW, RUS, 4829',
            amount=Decimal("-4320.4")
        ))
    }

    assert s.lines[3].__dict__ == {
        'amount': Decimal("9.01"),
        'check_no': None,
        'date': datetime.datetime(2019, 6, 17, 0, 0),
        'date_user': datetime.datetime(2019, 6, 16, 0, 0),
        'memo': 'SBERBANK ONL@IN VKLAD-KARTA , Moscow, RUS',
        'payee': None,
        'refnum': None,
        'trntype': 'DEBIT',
        'id': statement.generate_transaction_id(statement.StatementLine(
            date=datetime.datetime(2019, 6, 17, 0, 0),
            memo='SBERBANK ONL@IN VKLAD-KARTA , Moscow, RUS',
            amount=Decimal("9.01")
        ))
    }

    assert sum(l.amount for l in s.lines) == Decimal("7338.83")
