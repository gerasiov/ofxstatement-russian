#    AlfaBank (https://www.alfabank.ru) plugin for ofxstatement
#
#    Copyright 2017 Alexander Gerasiov <gq@cs.msu.su>
#    Copyright 2017,2020 Dmitry Pavlov <zeldigas@gmail.com>
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
import re
from decimal import Decimal

from ofxstatement import statement
from ofxstatement.parser import StatementParser
from ofxstatement.plugin import Plugin

# Тип счёта;Номер счета;Валюта;Дата операции;Референс проводки;Описание операции;Приход;Расход;

# file format options
delimiter = ';'
default_encoding = 'cp1251'
fieldnames = ['acc_name', 'acc', 'currency', 'op_time', 'refnum', 'description', 'income', 'withdraw']
type_map = {
    u"Комиссия за ": 'SRVCHG'
}


def parse_type(type, amount):
    for filter in type_map.keys():
        if type.startswith(filter):
            return type_map[filter]

    result = None

    if amount > 0:
        result = 'DEBIT'
    elif amount < 0:
        result = 'CREDIT'

    return result


class AlfabankStatementParser(StatementParser):
    statement = None

    def __init__(self, fin):
        super().__init__()
        self.date_format = '%d.%m.%y'
        self.statement = statement.Statement()
        self.fin = fin
        # Skip 1st row with column's headers
        self.fin.readline()
        self.cur_record = 1
        self.user_date = False

    def split_records(self):
        return csv.DictReader(self.fin, delimiter=delimiter, fieldnames=fieldnames)

    def parse_record(self, line):
        transaction = statement.StatementLine()

        if not self.statement.account_id:
            self.statement.account_id = line['acc']

        if not self.statement.currency:
            self.statement.currency = line['currency']

        if not line['currency'] == self.statement.currency:
            print("Transaction %s currency '%s' differ from account currency '%s'." % (
                line['op_time'], line['currency'], self.statement.currency))
            return None

        transaction.date = self.parse_datetime(line['op_time'])
        date_user = self.try_find_user_date(line['description'])

        if self.user_date and date_user:
            transaction.date = self.parse_datetime(date_user)

        transaction.amount = self.get_amount(line['income'], line['withdraw'])

        transaction.trntype = parse_type(line['description'], transaction.amount)
        transaction.refnum = line['refnum']

        transaction.memo = line['description']

        if transaction.trntype:
            return transaction
        else:
            return None

    def get_amount(self, income, withdraw):
        income_val = Decimal(income.replace(',', '.'))
        withdraw_val = Decimal(withdraw.replace(',', '.'))
        if income_val == 0:
            return -withdraw_val
        else:
            return income_val

    @staticmethod
    def try_find_user_date(param):
        date_pattern = '\\d{2}\\.\\d{2}\\.\\d{2}'
        m = re.search('{0} ({0})'.format(date_pattern), param)
        if m:
            return m.group(1)
        else:
            return None


class AlfabankPlugin(Plugin):
    """AlfaBank CSV (https://www.alfabank.ru)
    """

    def get_parser(self, fin):
        f = open(fin, 'r', encoding=self.settings.get('file_encoding', default_encoding))
        parser = AlfabankStatementParser(f)
        parser.statement.currency = self.settings.get('currency')
        parser.statement.account_id = self.settings.get('account')
        parser.statement.bank_id = self.settings.get('bank', 'Alfabank')
        parser.user_date = self.settings.get('user_date', 'true') == 'true'
        return parser
