# -*- coding: utf-8 -*-
__author__ = 'AminHP'

from .core import run
from .types import JudgementStatusType


def judge(code_path, prog_lang, testcase_dir, time_limit, space_limit):
    status, reason = run(code_path, prog_lang.name, testcase_dir, time_limit, space_limit)
    return status, reason
