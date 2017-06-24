~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Russian banks plugins for ofxstatement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`ofxstatement`_ is a tool to convert proprietary bank statement to OFX format,
suitable for importing to GnuCash. Plugin for ofxstatement parses a
particular proprietary bank statement format and produces common data
structure, that is then formatted into an OFX file.

`ofxstatement-russian`_ provides some Russian banks plugins for ofxstatement.

Supported banks:

* Avangard Bank (http://avangard.ru) plugin 'avangard'
* Tinkoff Bank (http://tinkoff.ru) plugin 'tinkoff'
* SberBank (http://sbrf.ru) plugin 'sberbank'


Avangard
--------

CSV statements for credit, debit or current account are supported.

Tinkoff
-------

CSV statement for credit, debit and saving account are supported.

SberBank
--------

TXT statement (available via "request statement by e-mail" function) for debit card is supported.

.. _ofxstatement: https://github.com/kedder/ofxstatement
.. _ofxstatement-russian: https://github.com/gerasiov/ofxstatement-russian


Plugin configuration parameters
===============================

avangard
--------

bank
        Bank id
        (default is 'Avangard')

account
        Account id

currency
        Currency
        (default is 'RUB')

tinkoff
-------

bank
        Bank id
        (default is 'Tinkoff')

account
        Account id

currency
        Currency
        (if not set, will be extracted from the first record)

sberbank
--------

bank
        Bank id
        (default is 'SberBank')

account
        Account id
        (if not set, will be extracted from the statement)

currency
        Currency
        (if not set, will be extracted from the statement)


Authors
=======
|  Copyright (c) 2013 Andrey Lebedev <andrey@lebedev.lt>
|  Copyright (c) 2016 Alexander Gerasiov <gq@cs.msu.su>
|

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as
published by the Free Software Foundation.
