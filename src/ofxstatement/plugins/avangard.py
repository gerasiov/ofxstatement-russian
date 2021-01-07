#    Avangard Bank (https://www.avangard.ru/) plugin for ofxstatement
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

from ofxstatement.parser import StatementParser
from ofxstatement.plugin import Plugin
from ofxstatement import statement
from datetime import datetime
import csv

# file format options
av_delimiter = ';'
av_time_format = '%d.%m.%Y %H:%M'
av_encoding = 'cp1251'
av_currency = 'RUB'
av_fieldnames = ['tr_time', 'debit', 'credit', 'type', 'op_time', 'card', 'currency_value',
                 'currency', 'MCC', 'description']
av_type_map = {
    u"Зачисление": 'CREDIT',
    u"Покупка": 'PAYMENT',
    u"Типовой платеж": 'PAYMENT',
    u"Возврат": 'CREDIT',
    u"Перечисление средств по поручению клиента.": 'XFER',
    u"Перевод с карты": 'XFER',
    u"Продажа клиенту валюты": 'XFER',
    u"Перечисление средств на вклад": 'XFER',
    u"Выплата суммы бонусов по карте": 'DIV',
    u"Перечисление процентов по вкладу": 'DIV',
    u"Внесение на картсчет.": 'DEP',
    u"Комиссия за осуществление трансграничной операции": 'FEE',
    u"Комиссия за конверсию по трансграничной операции": 'FEE',
    u"Комиссия за предоставление овердрафта": 'FEE',
    u"Комиссия за получение наличных": 'FEE',
    u"Комиссия за операцию": 'FEE',
    u"Комиссия за осуществление расчетов по операциям": 'SRVCHG',
    u"Погашение процентов по предоставленному овердрафту": 'FEE',
    u"Плата за прием и обработку платежных документов": 'FEE',
    u"Снятие со счета": 'CASH',
    u"Внесение на счет": 'DEP',
    u"Наличные": 'ATM',
    u"Погашение овердрафта": None,
    u"Предоставление овердрафта": None,
}


def parse_type(type, amount):
    for filter in av_type_map.keys():
        if type.startswith(filter):
            return av_type_map[filter]

    result = None

    if amount > 0:
        result = 'DEBIT'
    elif amount < 0:
        result = 'CREDIT'

    # print("Unknown type \"%s\", consider %s"%(type, result))
    return result


class AvangardStatementParser(StatementParser):
    statement = None

    def __init__(self, fin):
        super().__init__()
        self.statement = statement.Statement()
        self.fin = fin

    def split_records(self):
        return csv.DictReader(self.fin, delimiter=av_delimiter, fieldnames=av_fieldnames)

    def parse_record(self, line):
        transaction = statement.StatementLine()

        transaction.date = datetime.strptime(line[('op_time' if line['op_time'] else 'tr_time')],
                                             av_time_format)

        transaction.amount = (float(line['debit']) if line['debit'] else 0) - (
            float(line['credit']) if line['credit'] else 0)

        transaction.trntype = parse_type(line['type'], transaction.amount)

        transaction.memo = line['description'] if line['description'] else line['type']

        if line['MCC']:
            transaction.memo = "%s, %s" % (transaction.memo, line['MCC'])

        if line['card']:
            transaction.memo = "%s, %s" % (transaction.memo, line['card'])

        # as csv file does not contain explicit id of transaction, generating artificial one
        transaction.id = statement.generate_transaction_id(transaction)

        if transaction.trntype:
            return transaction
        else:
            return None


class AvangardPlugin(Plugin):
    """Avangard Bank CSV (http://avangard.ru)
    """

    def get_parser(self, fin):
        f = open(fin, 'r', encoding=av_encoding)
        parser = AvangardStatementParser(f)
        parser.statement.currency = self.settings.get('currency', av_currency)
        parser.statement.account_id = self.settings['account']
        parser.statement.bank_id = self.settings.get('bank', 'Avangard')
        return parser
