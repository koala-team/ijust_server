# -*- coding: utf-8 -*-
__author__ = ['SALAR', 'AminHP']

# python imports
import docker
import os
import imp
import re

# project imports
from .types import JudgementStatusType


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')


def run(code_path, prog_lang, testcase_dir, time_limit, space_limit):
    prog_lang = prog_lang.lower()
    pl_script_dir = os.path.join(SCRIPTS_DIR, prog_lang)
    input_dir = os.path.join(testcase_dir, 'inputs')
    output_dir = os.path.join(testcase_dir, 'outputs')
    log_dir = "%s.log" % code_path

    config_file = os.path.join(pl_script_dir, 'config.py')
    config_mod = imp.load_source('plconfig', config_file)

    time_limit = float(time_limit * config_mod.TIME_LIMIT_FACTOR)

    run_in_container(code_path, pl_script_dir, input_dir, log_dir, time_limit, space_limit)
    return check_result(log_dir, output_dir, time_limit, space_limit)



def run_in_container(code_path, pl_script_dir, input_dir, log_dir, time_limit, space_limit):
    code_filename = os.path.basename(code_path)

    volumes = {
        code_path: { 
            'bind': "/etc/data/%s" % code_filename,
            'mode': 'ro'
        },
        pl_script_dir: {
            'bind': "/etc/data/plscript",
            'mode': 'ro'
        },
        input_dir: {
            'bind': "/etc/data/inputs",
            'mode': 'ro'
        },
        log_dir: {
            'bind': "/etc/data/%s.log" % code_filename,
            'mode': 'rw'
        }
    }

    env = {
        "CODE_PATH": volumes[code_path]["bind"],
        "PL_SCRIPT_DIR": volumes[pl_script_dir]["bind"],
        "TESTCASE_DIR": volumes[input_dir]["bind"],
        "LOG_DIR": volumes[log_dir]["bind"],
        "TIME_LIMIT": time_limit
    }

    client = docker.from_env()
    try:
        client.containers.run(
            image = "ijudge",
            remove = True, 
            stdout = True,
            stderr = True,
            mem_limit = "%sMB" % (space_limit + 10),
            mem_swappiness = 0,
            cpu_quota = 100000,
            volumes = volumes,
            environment = env
        )
    except docker.errors.ContainerError:
        pass



def check_result(log_dir, output_dir, time_limit, space_limit):
    compile_error_fp = os.path.join(log_dir, "compile.err")

    ## check compile error
    st = check_compilation(compile_error_fp)
    if st is not None:
        return st, open(compile_error_fp).read()

    for testcase in sorted([tc for tc in os.listdir(output_dir)]):
        desired_output_fp = os.path.join(output_dir, testcase)
        code_output_fp = "%s.out" % os.path.join(log_dir, testcase)
        code_error_fp = "%s.err" % os.path.join(log_dir, testcase)
        code_stat_fp = "%s.stt" % os.path.join(log_dir, testcase)

        if not os.path.exists(code_error_fp):
            continue

        ## check time limit and space limit
        st = check_stat(code_stat_fp, time_limit, space_limit)
        if st is not None:
            return st, "testcase: %s" % testcase

        ## check runtime error
        st = check_error(code_error_fp)
        if st is not None:
            return st, "testcase: %s" % testcase

        ## check output
        st = check_output(code_output_fp, desired_output_fp)
        if st is not None:
            return st, "testcase: %s" % testcase

    return JudgementStatusType.Accepted, None


def check_compilation(compile_error_fp):
    if os.stat(compile_error_fp).st_size != 0:
        return JudgementStatusType.CompileError
    return None


def check_stat(code_stat_fp, time_limit, space_limit):
    stat = open(code_stat_fp).read()

    time = re.search('(Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): )(.*)\n', stat).group(2)
    time = float(time.split(':')[0]) * 60 + float(time.split(':')[1])

    space = re.search('(Maximum resident set size \(kbytes\): )(.*)\n', stat).group(2)
    space = float(space) / 1000.

    if time >= time_limit:
        return JudgementStatusType.TimeExceeded
    if space >= space_limit:
        return JudgementStatusType.SpaceExceeded
    return None


def check_error(code_error_fp):
    if os.stat(code_error_fp).st_size != 0:
        return JudgementStatusType.RuntimeError
    return None


def check_output(code_output_fp, desired_output_fp):
    output = open(code_output_fp).read()
    desired_output = open(desired_output_fp).read()

    if len(output):
        output = output[:-1] if output[-1] == '\n' else output
    desired_output = desired_output.strip()

    if output != desired_output:
        return JudgementStatusType.WrongAnswer
    return None
