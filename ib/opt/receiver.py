#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# Defines Receiver class to handle inbound data.
#
# The Receiver class is built programatically at runtime.  Message
# types are defined in the ib.opt.message module, and those types are
# used to construct methods on the Receiver class during its
# definition.  Refer to the ReceiverType metaclass and the
# ib.opt.message module more information.
#
##
from ib.lib.overloading import overloaded
from ib.opt.message import wrapperMethods


def messageMethod(name, parameters):
    """ Creates method for dispatching messages.

    @param name name of method as string
    @param parameters list of method argument names
    @return newly created method (as closure)
    """
    def dispatchMethod(self, *arguments):
        self.dispatcher(name, dict(list(zip(parameters, arguments))))
    dispatchMethod.__name__ = name
    return dispatchMethod


class ReceiverType(type):
    """ Metaclass to add EWrapper methods to Receiver class.

    When the Receiver class is defined, this class adds all of the
    wrapper methods to it.
    """
    def __new__(cls, name, bases, namespace):
        """ Creates a new type.

        @param name name of new type as string
        @param bases tuple of base classes
        @param namespace dictionary with namespace for new type
        @return generated type
        """
        for methodName, methodArgs in wrapperMethods:
            namespace[methodName] = messageMethod(methodName, methodArgs)
        return type(name, bases, namespace)


class Receiver(object, metaclass=ReceiverType):
    """ Receiver -> dispatches messages to interested callables

    Instances implement the EWrapper interface by way of the
    metaclass.
    """

    def __init__(self, dispatcher):
        """ Initializer.

        @param dispatcher message dispatcher instance
        """
        self.dispatcher = dispatcher

    @overloaded
    def error(self, e):
        """ Dispatch an error generated by the reader.

        Error message types can't be associated in the default manner
        with this family of methods, so we define these three here
        by hand.

        @param e some error value
        @return None
        """
        self.dispatcher('error', dict(errorMsg=e))

    @error.register(object, str)
    def error_0(self, strval):
        """ Dispatch an error given a string value.

        @param strval some error value as string
        @return None
        """
        self.dispatcher('error', dict(errorMsg=strval))

    @error.register(object, int, int, str)
    def error_1(self, id, errorCode, errorMsg):
        """ Dispatch an error given an id, code and message.

        @param id error id
        @param errorCode error code
        @param errorMsg error message
        @return None
        """
        params = dict(id=id, errorCode=errorCode, errorMsg=errorMsg)
        self.dispatcher('error', params)
