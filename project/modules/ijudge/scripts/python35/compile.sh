#! /bin/bash

CMD="compile(open('$CODE_PATH').read(), '$CODE_PATH', 'exec')"
python3.5 -c "$CMD"
