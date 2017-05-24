#! /bin/bash

TARGET=$COMPILED_DIR/a.out

g++ -static -fno-optimize-sibling-calls -fno-strict-aliasing -DONLINE_JUDGE -lm -s -x c++ \
	-O2 -w -o $TARGET $CODE_PATH
