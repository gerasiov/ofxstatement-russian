import doctest

from ofxstatement.plugins.vtb import VtbStatementParser


def doctest_VtbParser():
    """Test VtbStatementParser

    Lets define VTB sample csv to parse and write it to file-like object

        >>> import io
        >>> csv = '''Начало периода;2019-07-07
        ... Конец периода;2019-07-13
        ...
        ... Выписка по счету/карте;Номер
        ... Карта с кредитной составляющей;'462235******0069
        ...
        ...
        ... Валюта;Баланс на конец периода;Поступления;Списания;Заблокировано
        ... RUR;82 604,01;0,00;-17 351,00;-2 426,96
        ...
        ...
        ... Номер карты/счета/договора;Дата операции;Дата обработки;Сумма операции;Валюта операции;Сумма пересчитанная в валюту счета;Валюта счета;Основание;Статус
        ... '462235******7428;2019-07-06 00:00:00;2019-07-08;-4,50;EUR;-336,15;RUR;Карта *1234 payee1;Исполнено
        ... '462235******7428;2019-07-06 00:00:00;2019-07-07;-3,80;EUR;-283,48;RUR;Карта *1234 payee2;Исполнено
        ... '462235******7428;2019-07-05 00:00:00;2019-07-07;-300,00;RUR;-300,00;RUR;Карта *1234 PAY MTS RU TOPUP 1234;Исполнено
        ... '462235******7428;2019-07-13 10:48:55;;-600,00;RUR;-600,00;RUR;Карта *1234 MEGAFON TOPUP  1234;В обработке
        ... '''
        >>> f = io.StringIO(csv)

    Create and configure csv parser:
        >>> parser = VtbStatementParser(f)
        >>> parser.statement.bank_id = 'VTB'

    And parse csv:
        >>> statement = parser.parse()
        >>> statement.account_id
        '462235******0069'
        >>> statement.start_date
        datetime.datetime(2019, 7, 7, 0, 0)
        >>> statement.end_date
        datetime.datetime(2019, 7, 13, 0, 0)
        >>> statement.start_balance
        Decimal('99955.01')
        >>> statement.end_balance
        Decimal('82604.01')
        >>> len(statement.lines)
        4
        >>> statement.lines[0].amount
        Decimal('-336.15')
        >>> statement.lines[0].memo
        'Карта *1234 payee1'
        >>> statement.lines[0].date
        datetime.datetime(2019, 7, 8, 0, 0)
        >>> statement.lines[0].payee
        'payee1'

        >>> statement.lines[1].amount
        Decimal('-283.48')
        >>> statement.lines[1].date
        datetime.datetime(2019, 7, 7, 0, 0)
        >>> statement.lines[1].memo
        'Карта *1234 payee2'
        >>> statement.lines[1].payee
        'payee2'

        >>> statement.lines[2].amount
        Decimal('-300.00')
        >>> statement.lines[2].memo
        'Карта *1234 PAY MTS RU TOPUP 1234'
        >>> statement.lines[2].date
        datetime.datetime(2019, 7, 7, 0, 0)
        >>> statement.lines[2].payee
        'PAY MTS RU TOPUP 1234'

        >>> statement.lines[3].amount
        Decimal('-600.00')
        >>> statement.lines[3].memo
        'Карта *1234 MEGAFON TOPUP  1234'
        >>> statement.lines[3].date
        >>> statement.lines[3].payee
        'MEGAFON TOPUP  1234'

    """


def doctest_VtbParser_userdates():
    """Test generic VtbStatementParser

    Lets define VTB sample csv to parse and write it to file-like object

        >>> import io
        >>> csv = '''Начало периода;2019-07-07
        ... Конец периода;2019-07-13
        ...
        ... Выписка по счету/карте;Номер
        ... Карта с кредитной составляющей;'462235******0069
        ...
        ...
        ... Валюта;Баланс на конец периода;Поступления;Списания;Заблокировано
        ... RUR;82 604,01;0,00;-17 351,00;-2 426,96
        ...
        ...
        ... Номер карты/счета/договора;Дата операции;Дата обработки;Сумма операции;Валюта операции;Сумма пересчитанная в валюту счета;Валюта счета;Основание;Статус
        ... '462235******7428;2019-07-06 00:00:00;2019-07-08;-4,50;EUR;-336,15;RUR;Карта *1234 payee1;Исполнено
        ... '''
        >>> f = io.StringIO(csv)

    Create and configure csv parser:
        >>> parser = VtbStatementParser(f)
        >>> parser.statement.bank_id = 'VTB'
        >>> parser.user_date = True

    And parse csv:
        >>> statement = parser.parse()
        >>> len(statement.lines)
        1
        >>> statement.lines[0].amount
        Decimal('-336.15')
        >>> statement.lines[0].memo
        'Карта *1234 payee1'
        >>> statement.lines[0].date
        datetime.datetime(2019, 7, 6, 0, 0)
    """

def test_suite(*args):
    return doctest.DocTestSuite(optionflags=(doctest.NORMALIZE_WHITESPACE|
                                             doctest.ELLIPSIS|
                                             doctest.REPORT_ONLY_FIRST_FAILURE|
                                             doctest.REPORT_NDIFF
                                             ))