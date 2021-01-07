#    SberBank (https://www.sberbank.ru/) CSV plugin for ofxstatement
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
from decimal import Decimal

from ofxstatement.parser import StatementParser
from ofxstatement.plugin import Plugin
from ofxstatement import statement
from datetime import datetime

# file format options
SB_DELIMITER = ';'
SD_TIME_FORMAT = '%d.%m.%Y'
SD_ENCODING = 'utf-8'
SB_FIELDNAMES = ['card_type', 'card_num', 'date_user', 'date', 'auth_code', 'op_type', 'op_city',
                 'op_country', 'description', 'currency', 'currency_amount', 'amount']


class SberBankCSVStatementParser(StatementParser):
    statement = None

    def __init__(self, fin):
        super().__init__()
        self.statement = statement.Statement()
        self.fin = fin
        # Skip 1st row with column's headers
        self.fin.readline()
        self.cur_record = 1

    def split_records(self):
        return csv.DictReader(self.fin, delimiter=SB_DELIMITER, fieldnames=SB_FIELDNAMES)

    def parse_record(self, line):
        transaction = statement.StatementLine()

        if not self.statement.account_id:
            self.statement.account_id = '{} {}'.format(line['card_type'], line['card_num'])

        transaction.date = datetime.strptime(line['date'], SD_TIME_FORMAT)
        transaction.date_user = datetime.strptime(line['date_user'], SD_TIME_FORMAT)

        transaction.amount = Decimal(line['amount'].replace(',', '.'))

        transaction.trntype = 'DEBIT' if transaction.amount > 0 else 'CREDIT'

        transaction.memo = ', '.join(line[f] for f in
                                     ('description', 'op_city', 'op_country', 'op_type') if line[f])

        # as csv file does not contain explicit id of transaction, generating artificial one
        transaction.id = statement.generate_transaction_id(transaction)

        return transaction


class SberBankCSVPlugin(Plugin):
    """SberBank CSV (http://sberbank.ru)
    """

    def get_parser(self, fin):
        f = open(fin, 'r', encoding=SD_ENCODING)
        parser = SberBankCSVStatementParser(f)
        parser.statement.currency = self.settings.get('currency')
        parser.statement.account_id = self.settings.get('account')
        parser.statement.bank_id = self.settings.get('bank', 'SberBank')
        return parser
