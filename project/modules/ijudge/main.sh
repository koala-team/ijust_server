#! /bin/bash

echo "hello!!!"
set -e

export COMPILED_DIR="/tmp/compiled"


if [ ! -d "$COMPILED_DIR" ]; then
	mkdir "$COMPILED_DIR"
fi

if [ -z "$CODE_PATH" ]; then
	echo "please export CODE_PATH environmet"
	exit 1
fi

if [ -z "$TESTCASE_DIR" ]; then
	echo "please export TESTCASE_DIR files directory"
	exit 1
fi

if [ -z "$LOG_DIR" ]; then
	export LOG_DIR="/tmp/outputs"
fi

if [ ! -d "$LOG_DIR" ]; then
		mkdir "$LOG_DIR"
	fi

echo "begin compiling"


if [ -s "$CODE_PATH" ]; then

	/bin/bash "$PL_SCRIPT_DIR/compile.sh" 2> "$LOG_DIR/compile.err"

	echo "compiled successfully"
	echo "begin tests"

	for tc in "$TESTCASE_DIR"/*
	do
		if [ -s "$tc" ]; then
			NAME="$(basename $tc)"
			ulimit -s hard
			/usr/bin/time -v -o "$LOG_DIR/$NAME.stt" runuser -u restricted_user timeout "$TIME_LIMIT"s \
				/bin/bash "$PL_SCRIPT_DIR/run.sh" < "$tc" 1> "$LOG_DIR/$NAME.out" 2> "$LOG_DIR/$NAME.err"
		fi
	done
	echo "end of tests"

else
	echo "there is nothing for compile"
fi

if [ -d "COMPILED_DIR" ]; then
	echo "begin of remove compiled file"
	rm -rf "$COMPILED_DIR/*"
fi

echo "end"
