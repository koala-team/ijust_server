#! /bin/bash

TARGET=$COMPILED_DIR/a.out

g++ -fno-optimize-sibling-calls -fno-strict-aliasing -DONLINE_JUDGE -lm -s -x c++ \
	-O2 -w -std=c++0x -o $TARGET $CODE_PATH
