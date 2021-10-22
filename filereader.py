from __future__ import print_function
import os
import sys
import yaml


def _default_error_handler(community):
    print("Invalid YAML: %s" % community, file=sys.stderr)


def get_communities_data(srcdir, exclude,
                         error_handler=_default_error_handler):
    for fname in sorted(list(set(os.listdir(srcdir)) - set(exclude))):
        if fname.startswith("."):
            continue

        if fname.startswith("README"):
            continue

        fpath = os.path.join(srcdir, fname)
        if os.path.isfile(fpath):
            with open(fpath) as f:
                try:
                    data = yaml.safe_load(f)
                except yaml.YAMLError:
                    error_handler(fname)
                    continue
            yield (fname, data)
