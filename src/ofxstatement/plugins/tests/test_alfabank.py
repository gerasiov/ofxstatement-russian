import doctest

from ofxstatement.plugins.alfabank import AlfabankStatementParser

def doctest_AlfaParser():
    """Test generic CsvStatementParser

    Lets define alfabank sample csv to parse and write it to file-like object

        >>> import io
        >>> csv = '''
        ... Мой счет;11111111111111111111;RUR;31.05.17;ABCDEF11111111111;{VO11111} Перечисление ден. средств (зарплата за май 2017 г.);33123,56;0;
        ... Мой счет;11111111111111111111;RUR;03.05.17;ABCDEF22222222222;Комиссия за переводы в рублях за период с1МАЙ17 по 1МАЙ17 поруч.поданы ч/з ИнтернетБанк Согл.тариф.Банка Иванов Иван Иванович;0;50;
        ... Мой счет;11111111111111111111;RUR;03.05.17;ABC_1AA11A;123456++++++6789    11111111\\\\123\\\\Visa Direct\\\\SOME BANK             03.05.17 01.05.17    1500.00  RUR MCC1234;0;1500;
        ... '''
        >>> f = io.StringIO(csv)

    Create and configure csv parser:
        >>> parser = AlfabankStatementParser(f)
        >>> parser.statement.bank_id = 'Alfabank'

    And parse csv:
        >>> statement = parser.parse()
        >>> statement.account_id
        '11111111111111111111'
        >>> statement.currency
        'RUR'
        >>> len(statement.lines)
        3
        >>> statement.lines[0].amount
        Decimal('33123.56')
        >>> statement.lines[0].memo
        '{VO11111} Перечисление ден. средств (зарплата за май 2017 г.)'
        >>> statement.lines[0].refnum
        'ABCDEF11111111111'
        >>> statement.lines[0].date
        datetime.datetime(2017, 5, 31, 0, 0)
        >>> statement.lines[0].trntype
        'DEBIT'

        >>> statement.lines[1].amount
        Decimal('-50')
        >>> statement.lines[1].date
        datetime.datetime(2017, 5, 3, 0, 0)
        >>> statement.lines[1].memo
        'Комиссия за переводы в рублях за период с1МАЙ17 по 1МАЙ17 поруч.поданы ч/з ИнтернетБанк Согл.тариф.Банка Иванов Иван Иванович'
        >>> statement.lines[1].trntype
        'SRVCHG'

        >>> statement.lines[2].amount
        Decimal('-1500')
        >>> statement.lines[2].memo
        '123456++++++6789    11111111\\\\123\\\\Visa Direct\\\\SOME BANK             03.05.17 01.05.17    1500.00  RUR MCC1234'
        >>> statement.lines[2].date
        datetime.datetime(2017, 5, 3, 0, 0)
        >>> statement.lines[2].trntype
        'CREDIT'

    """

def doctest_AlfaParser_userdates():
    """Test generic CsvStatementParser

    Lets define alfabank sample csv to parse and write it to file-like object

        >>> import io
        >>> csv = '''
        ... Мой счет;11111111111111111111;RUR;03.05.17;ABC_1AA11A;123456++++++6789    11111111\\\\123\\\\Visa Direct\\\\SOME BANK             03.05.17 01.05.17    1500.00  RUR MCC1234;0;1500;
        ... '''
        >>> f = io.StringIO(csv)

    Create and configure csv parser:
        >>> parser = AlfabankStatementParser(f)
        >>> parser.statement.bank_id = 'Alfabank'
        >>> parser.user_date = True

    And parse csv:
        >>> statement = parser.parse()
        >>> len(statement.lines)
        1
        >>> statement.lines[0].amount
        Decimal('-1500')
        >>> statement.lines[0].memo
        '123456++++++6789    11111111\\\\123\\\\Visa Direct\\\\SOME BANK             03.05.17 01.05.17    1500.00  RUR MCC1234'
        >>> statement.lines[0].date
        datetime.datetime(2017, 5, 1, 0, 0)
    """


def test_suite(*args):
    return doctest.DocTestSuite(optionflags=(doctest.NORMALIZE_WHITESPACE|
                                             doctest.ELLIPSIS|
                                             doctest.REPORT_ONLY_FIRST_FAILURE|
                                             doctest.REPORT_NDIFF
                                             ))