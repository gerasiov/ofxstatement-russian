#    Tinkoff Bank (https://tinkoff.ru) plugin for ofxstatement
#
#    Copyright 2013 Andrey Lebedev <andrey@lebedev.lt>
#    Copyright 2016 Alexander Gerasiov <gq@cs.msu.su>
#    Copyright 2020 Dmitry Pavlov <zeldigas@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import csv
from datetime import datetime
from decimal import Decimal

from ofxstatement.parser import StatementParser
from ofxstatement.plugin import Plugin
from ofxstatement import statement


# file format options
t_delimiter = ';'
t_time_format = '%d.%m.%Y %H:%M:%S'
t_encoding = 'cp1251'
t_fieldnames = ['op_time', 'tr_time', 'card', 'status', 'op_amount', 'op_currency', 'amount',
                'currency', 'cashback', 'category', 'MCC', 'description', 'bonus']
t_type_map = {
    u"Капитализация": 'DIV',
    u"Вознаграждение за операции покупок": 'DIV',
    u"Пополнение. Тинькофф Банк. Бонус": 'DIV',
    u"Проценты на остаток по счету": 'DIV',
    u"Плата за обслуживание": 'SRVCHG',
    u"Комиссия за выдачу наличных": 'SRVCHG',
    u"Снятие наличных": 'ATM',
    u"Пополнение": 'XFER',
    u"На счет в другом банке": 'XFER',
    u"Перевод c карты другого банка": 'XFER',
    u"Изъятие вклада при закрытии.": 'XFER',
    u"Внешний банковский перевод": 'XFER',
}


def parse_type(type, amount):
    for filter in t_type_map.keys():
        if type.startswith(filter):
            return t_type_map[filter]

    result = None

    if amount > 0:
        result = 'DEBIT'
    elif amount < 0:
        result = 'CREDIT'

    # print("Unknown type \"%s\", consider %s"%(type, result))
    return result


class TinkoffStatementParser(StatementParser):
    statement = None

    def __init__(self, fin):
        super().__init__()
        self.statement = statement.Statement()
        self.fin = fin
        # Skip 1st row with column's headers
        self.fin.readline()
        self.cur_record = 1

    def split_records(self):
        return csv.DictReader(self.fin, delimiter=t_delimiter, fieldnames=t_fieldnames)

    def parse_record(self, line):
        transaction = statement.StatementLine()

        if not line['status'] == 'OK':
            print("Notice: Skipping line %d: Transaction time %s status is %s." % (
                self.cur_record, line['op_time'], line['status']))
            return None

        if not self.statement.currency:
            self.statement.currency = line['currency']

        if not line['currency'] == self.statement.currency:
            print("Transaction %s currency '%s' differ from account currency '%s'." % (
                line['op_time'], line['currency'], self.statement.currency))
            return None

        transaction.date = datetime.strptime(line['op_time'], t_time_format)

        transaction.amount = Decimal(line['amount'].replace(',', '.'))

        transaction.trntype = parse_type(line['description'], transaction.amount)

        transaction.memo = "%s: %s" % (line['category'], line['description'])

        self._append_to_memo(transaction, line, 'MCC')
        self._append_to_memo(transaction, line, 'card')

        # as csv file does not contain explicit id of transaction, generating artificial one
        transaction.id = statement.generate_transaction_id(transaction)

        if transaction.trntype:
            return transaction
        else:
            return None

    @staticmethod
    def _append_to_memo(transaction, line, field):
        if line[field]:
            transaction.memo = "%s, %s" % (transaction.memo, line[field])



class TinkoffPlugin(Plugin):
    """Tinkoff Bank CSV (http://tinkoff.ru)
    """

    def get_parser(self, fin):
        f = open(fin, 'r', encoding=t_encoding)
        parser = TinkoffStatementParser(f)
        parser.statement.currency = self.settings.get('currency')
        parser.statement.account_id = self.settings['account']
        parser.statement.bank_id = self.settings.get('bank', 'Tinkoff')
        return parser
