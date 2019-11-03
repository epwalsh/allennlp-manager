#!/bin/bash

if [[ $ALLENNLP_VERSION == 'nightly' ]]; then
    pip install --no-cache-dir 'git+git://github.com/allenai/allennlp.git#egg=allennlp'
elif [[ $ALLENNLP_VERSION == 'stable' ]]; then
    pip install --no-cache-dir allennlp
else
    pip install --no-cache-dir allennlp=="$ALLENNLP_VERSION"
fi
