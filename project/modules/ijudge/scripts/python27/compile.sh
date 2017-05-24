#! /bin/bash

CMD="compile(open('$CODE_PATH').read(), '$CODE_PATH', 'exec')"
python2.7 -c "$CMD"
