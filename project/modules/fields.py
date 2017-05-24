# -*- coding: utf-8 -*-
__author__ = 'AminHP'

# python imports
from mongoengine import IntField


class EnumField(object):
    """
    A class to register Enum type (from the package enum34) into mongo
    :param choices: must be of :class:`enum.Enum`: type
        and will be used as possible choices
    """

    def __init__(self, enum, *args, **kwargs):
        self.enum = enum
        kwargs['choices'] = [choice for choice in enum]
        super(EnumField, self).__init__(*args, **kwargs)

    def __get_value(self, enum):
        return enum.value if hasattr(enum, 'value') else enum

    def to_python(self, value):
        return self.enum(super(EnumField, self).to_python(value))

    def to_mongo(self, value):
        return self.__get_value(value)

    def prepare_query_value(self, op, value):
        return super(EnumField, self).prepare_query_value(
                op, self.__get_value(value))

    def validate(self, value):
        return super(EnumField, self).validate(self.__get_value(value))

    def _validate(self, value, **kwargs):
        return super(EnumField, self)._validate(
                self.enum(self.__get_value(value)), **kwargs)


class IntEnumField(EnumField, IntField):
    """A variation on :class:`EnumField` for only int containing enumeration.
    """
    pass
