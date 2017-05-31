#!/usr/bin/env python

# Copyright (C) 2005-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#                         slmm <noreply@example.com>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Application wide events are managed here.
"""

from __future__ import absolute_import
from zope import interface
from gaphor.interfaces import *


@interface.implementer(IServiceEvent)
class ServiceInitializedEvent(object):
    """
    This event is emitted every time a new service has been initialized.
    """

    def __init__(self, name, service):
        self.name = name
        self.service = service


@interface.implementer(IServiceEvent)
class ServiceShutdownEvent(object):
    """
    This event is emitted every time a service has been shut down.
    """

    def __init__(self, name, service):
        self.name = name
        self.service = service


@interface.implementer(ITransactionEvent)
class TransactionBegin(object):
    """
    This event denotes the beginning of a transaction.
    Nested (sub-) transactions should not emit this signal.
    """


@interface.implementer(ITransactionEvent)
class TransactionCommit(object):
    """
    This event is emitted when a transaction (toplevel) is successfully
    commited.
    """


@interface.implementer(ITransactionEvent)
class TransactionRollback(object):
    """
    If a set of operations fail (e.i. due to an exception) the transaction
    should be marked for rollback. This event is emitted to tell the operation
    has failed.
    """


@interface.implementer(IActionExecutedEvent)
class ActionExecuted(object):
    """
    Once an operation has succesfully been executed this event is raised.
    """

    def __init__(self, name, action):
        self.name = name
        self.action = action

# vim:sw=4:et:ai
