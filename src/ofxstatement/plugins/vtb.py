#    VTB (https://www.vtb.ru/) plugin for ofxstatement
#
#    Copyright 2019 Rashit Azizbaev <syndicut@gmail.com>
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

from ofxstatement.parser import StatementParser
from ofxstatement.plugin import Plugin
from ofxstatement import statement

import csv
from decimal import Decimal
from datetime import datetime

default_encoding = 'cp1251'
delimiter = ';'
operation_date_format = '%Y-%m-%d %H:%M:%S'

dates_skip_lines = 2
statement_info_skip_lines = 3
balance_info_skip_lines = 3

dates_fieldnames = [
    'name',
    'value',
]

statement_info_fieldnames = [
    'type',
    'account_id',
]

balance_info_fieldnames = [
    'currency',
    'end_balance',
    'income',
    'withdrawl',
    'blocked',
]

records_fieldnames = [
    'account_id',
    'operation_date',
    'processing_date',
    'operation_amount',
    'operation_currency',
    'account_amount',
    'account_currency',
    'reason',
    'status',
]

statuses = {
    'PROCESSING': 'В обработке',
}

card_info_prefix = "Карта *"
card_info_prefix_len = len(card_info_prefix)+5


class VtbStatementParser(StatementParser):

    statement = None

    def __init__(self, fin):
        super().__init__()
        self.statement = statement.Statement()
        self.fin = fin
        self.user_date = False

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """
        dates_reader = csv.DictReader(self.fin, delimiter=delimiter, fieldnames=dates_fieldnames)
        start_date_entry = next(dates_reader)
        end_date_entry = next(dates_reader)
        self.statement.start_date = self.parse_datetime(start_date_entry['value'])
        self.statement.end_date = self.parse_datetime(end_date_entry['value'])

        self.skip_lines(dates_skip_lines)

        statement_info_reader = csv.DictReader(self.fin, delimiter=delimiter, fieldnames=statement_info_fieldnames)
        statement_info_entry = next(statement_info_reader)
        if self.statement.account_id is None:
            self.statement.account_id = self.parse_account_id(statement_info_entry['account_id'])

        self.skip_lines(statement_info_skip_lines)

        balance_info_reader = csv.DictReader(self.fin, delimiter=delimiter, fieldnames=balance_info_fieldnames)
        balance_info_item = next(balance_info_reader)
        if self.statement.currency is None:
            self.statement.currency = balance_info_item['currency']

        self.statement.end_balance = self._parse_decimal(balance_info_item['end_balance'])
        self.statement.start_balance = self.statement.end_balance - sum((self._parse_decimal(balance_info_item['income']),
                                                                         self._parse_decimal(balance_info_item['withdrawl'])))

        self.skip_lines(balance_info_skip_lines)

        super(VtbStatementParser, self).parse()
        return self.statement

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        return csv.DictReader(self.fin, delimiter=delimiter, fieldnames=records_fieldnames)

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """
        transaction = statement.StatementLine()

        transaction.date_user = datetime.strptime(line['operation_date'], operation_date_format)
        if line['status'] != statuses['PROCESSING']:
            if self.user_date:
                transaction.date = transaction.date_user
            else:
                transaction.date = self.parse_datetime(line['processing_date'])
        transaction.memo = line['reason']
        transaction.amount = self._parse_decimal(line['account_amount'])
        transaction.payee = self.parse_payee(line['reason'])
        transaction.trntype = self.parse_type(transaction.amount)

        # as csv file does not contain explicit id of transaction, generating artificial one
        # using operation date as main date in all cases
        transaction.id = statement.generate_transaction_id(statement.StatementLine(
            date=transaction.date_user, memo=transaction.memo, amount=transaction.amount
        ))

        return transaction

    @staticmethod
    def parse_account_id(value):
        return value.lstrip("'")

    @staticmethod
    def parse_payee(reason):
        if reason.startswith(card_info_prefix):
            return reason[card_info_prefix_len:]
        else:
            return reason

    @staticmethod
    def parse_type(amount):
        result = 'CHECK'
        if amount > 0:
            result = 'DEBIT'
        elif amount < 0:
            result = 'CREDIT'

        return result

    def skip_lines(self, lines_count):
        for _ in range(lines_count):
            next(self.fin)

    @staticmethod
    def _parse_decimal(value):
        # some plugins pass localised numbers, clean them up
        return Decimal(value.replace(",", ".").replace(" ", ""))


class VtbPlugin(Plugin):
    """VTB bank CSV (https://www.vtb.ru)
    """

    def get_parser(self, fin):
        f = open(fin, 'r', encoding=self.settings.get('file_encoding', default_encoding))
        parser = VtbStatementParser(f)
        parser.statement.currency = self.settings.get('currency')
        parser.statement.account_id = self.settings.get('account')
        parser.statement.bank_id = self.settings.get('bank', 'VTB')
        parser.user_date = self.settings.get('user_date', 'false') == 'true'
        return parser
