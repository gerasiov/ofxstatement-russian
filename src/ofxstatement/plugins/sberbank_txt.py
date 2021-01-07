#    SberBankTxt (https://www.sberbank.ru/) plugin for ofxstatement
#
#    Copyright 2013 Andrey Lebedev <andrey@lebedev.lt>
#    Copyright 2016 Alexander Gerasiov <gq@cs.msu.su>
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
import re

# file format options
sb_encoding = 'cp1251'


class ParserState:
    name = ""
    matchers = None

    def __init__(self, name, parser):
        self.name = name
        self.matchers = list()
        parser.append(self)

    def addMatcher(self, reString, nextState=None, function=None):
        self.matchers.append([re.compile(reString), nextState, function])

    def run(self, line):
        for (matcher, nextState, function) in self.matchers:
            match = matcher.match(line)
            if match:
                if function:
                    function(match)
                return nextState
        return None

    def __str__(self):
        string = "State '%s' matchers:\n" % self.name
        for matcher in self.matchers:
            string += "re '%s' => state '%s'\n" % (matcher[0], matcher[1])
        return string


class SberBankTxtStatementParser(StatementParser):
    statement = None

    transaction = None
    account_id = ""
    account_fl_len = 0

    machine = {}
    currentState = None
    internal = None

    def append(self, state):
        self.machine[state.name] = state

    def extractCurrency(self, match):
        if not self.statement.currency:
            self.statement.currency = match.group(1)

    def extractBeginBalance(self, match):
        if not self.statement.start_balance:
            self.statement.start_balance = float(match.group(1))

    def extractEndBalance(self, match):
        if not self.statement.end_balance:
            self.statement.end_balance = float(match.group(1))
        if not self.statement.account_id:
            self.statement.account_id = " ".join(self.account_id.split())
        if self.transaction:
            self.transaction.memo = " ".join(self.transaction.memo.split())
            self.statement.lines.append(self.transaction)
            self.transaction = None

    def parseDate(self, string):
        rusMonths = {
            u'ЯНВ': 1,
            u'ФЕВ': 2,
            u'МАР': 3,
            u'АПР': 4,
            u'МАЙ': 5,
            u'ИЮН': 6,
            u'ИЮЛ': 7,
            u'АВГ': 8,
            u'СЕН': 9,
            u'ОКТ': 10,
            u'НОЯ': 11,
            u'ДЕК': 12,
        }
        return datetime(2000 + int(string[5:]), rusMonths[string[2:5]], int(string[:2]))

    def extractTransaction(self, match):
        if self.transaction:
            self.transaction.memo = " ".join(self.transaction.memo.split())
            self.statement.lines.append(self.transaction)

        self.transaction = statement.StatementLine()

        self.account_fl_len = len(match.group(1))

        self.transaction.date = self.parseDate(match.group(3))
        self.transaction.memo = match.group(4)
        self.transaction.amount = float(match.group(5)) * (1 if match.group(6) else -1)
        self.transaction.trntype = 'DEBIT' if match.group(6) else 'CREDIT'
        if match.group(1).strip():
            self.account_id += match.group(1)

    def extractTransactionAppend(self, match):
        first = match.group(1)[:self.account_fl_len]
        second = match.group(1)[self.account_fl_len:]
        self.account_id += first
        self.transaction.memo += second

    def __init__(self, fin):
        self.statement = statement.Statement()
        self.internal = {}
        self.fin = fin

        self.currentState = 'init'

        state = ParserState('init', self)
        state.addMatcher(r"^.*ВАЛЮТА СЧЕТА.*$", 'currency')

        state = ParserState('currency', self)
        state.addMatcher(r"^\s*(\w{3})\s*$",
                         'begin_balance',
                         self.extractCurrency)

        state = ParserState('begin_balance', self)
        state.addMatcher(r"^ОСТАТОК НА НАЧАЛО ПЕРИОДА:\s*(\d+\.\d{2})(\+)?\s*$",
                         'table_header',
                         self.extractBeginBalance)

        state = ParserState('table_header', self)
        state.addMatcher(r"^[-+]{80,}$", 'table_header2')

        state = ParserState('table_header2', self)
        state.addMatcher(r"^[-+]{80,}$", 'transaction')

        state = ParserState('transaction', self)
        state.addMatcher(r"^[-+]{80,}$", 'end_balance')
        state.addMatcher(
            r"^(.*)\s*(\d{2}[А-Я]{3})\s+(\d{2}[А-Я]{3}\d{2})\s+\d{6}\s+(.*)\s\w{3}\s+\d*\.\d{2}\s+(\d*\.\d{2})(CR)?\s*$",
            None,
            self.extractTransaction)
        state.addMatcher(
            r"^(.*)\s*(\d{2}[А-Я]{3})\s+(\d{2}[А-Я]{3}\d{2})\s+\d{6}\s+(КОМИССИЯ)\s+(\d*\.\d{2})(CR)?\s*$",
            None,
            self.extractTransaction)
        state.addMatcher(
            r"^(.*)\s*(\d{2}[А-Я]{3})\s+(\d{2}[А-Я]{3}\d{2})\s+\d{6}\s+(.*)\s(\d*\.\d{2})(CR)?\s*$",
            None,
            self.extractTransaction)
        state.addMatcher(r".*ИТОГО ПО.*")
        state.addMatcher(r"^(.+)\s*$",
                         None,
                         self.extractTransactionAppend)

        state = ParserState('end_balance', self)
        state.addMatcher(r"^ОСТАТОК НА КОНЕЦ ПЕРИОДА:\s*(\d+\.\d{2})\+?\s*$",
                         'table_header',
                         self.extractEndBalance)

    def run(self, line):
        nextState = self.machine[self.currentState].run(line)
        if nextState:
            self.currentState = nextState

    def parse(self):
        for line in self.fin:
            self.run(line)

        return self.statement


class SberBankTxtPlugin(Plugin):
    """SberBank TXT (http://sbrf.ru)
    """

    def get_parser(self, fin):
        f = open(fin, 'r', encoding=sb_encoding)
        parser = SberBankTxtStatementParser(f)
        parser.statement.currency = self.settings.get('currency', None)
        parser.statement.account_id = self.settings.get('account', None)
        parser.statement.bank_id = self.settings.get('bank', 'SberBank')
        return parser
