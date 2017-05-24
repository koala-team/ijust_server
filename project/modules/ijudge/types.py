# -*- coding: utf-8 -*-
__author__ = 'AminHP'

from enum import Enum


class JudgementStatusType(Enum):
    Pending = 0
    Accepted = 1
    CompileError = 2
    WrongAnswer = 3
    TimeExceeded = 4
    SpaceExceeded = 5
    RuntimeError = 6
    RestrictedFunction = 7
    ExtensionError = 8


class ProgrammingLanguageType(Enum):
    Cpp = 0
    Cpp11 = 1
    Python27 = 2
    Python35 = 3
    Java8 = 4
