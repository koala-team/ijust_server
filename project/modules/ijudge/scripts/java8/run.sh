#! /bin/bash

CLASS_NAME=$(basename "${CODE_PATH%.*}")
TARGET=$CLASS_NAME

java -Djava.security.manager -Djava.security.policy=java.policy \
	-Xmx1000g -DONLINE_JUDGE=true -Duser.language=en \
	-Duser.region=US -Duser.variant=US -cp $COMPILED_DIR $TARGET
