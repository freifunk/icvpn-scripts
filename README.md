icvpn-scripts
=============
[![Build Status][Travis image]][Travis]

[Travis image]: https://travis-ci.org/freifunk/icvpn-scripts.svg
[Travis]: https://travis-ci.org/freifunk/icvpn-scripts

This is a collection of scripts for working with the [icvpn-meta repository].
While the actual data about the communities' networks and stuff goes there,
these scripts use that data to do something with it.

### Why is this a separate repository?
While the [icvpn-meta repository] is intended to be updated automatically to
receive updated data, it is obviously not a good idea to automatically update
the scripts that are periodically executed on a server. To prevent people from
shooting themselves in the foot by not reading a readme that says "copy the
scripts, don't use them directly!", the scripts were split off into this
repository.


Requirements
------------
All of the scripts are currently written in Python and need the `python-yaml`
package.

All of the scripts need a checked out version of the [icvpn-meta repository],
and expect it by default to be in the subdirectory `data` of the current
working directory. However, they all support the `-s` or `--source` switch to
specify another location.

### Debian
On Debian `apt-get install python3-yaml python3-requests python3-prettytable
python3-jinja2 python3-natsort` should install all dependencies.

#### Debian Wheezy (oldstable)
You might run into problems because of a missing ipaddress and natsort module (shipped with python >= 3.3), so install it via pip.
```
apt-get install python3-yaml python3-pip
pip-3.2 install ipaddress natsort
```


Find Free Resources (`findfree`)
--------------------------------
`findfree` searches for free asn, transfer ip combinations and ip subnet allocations in the predefined
network segments.

**Note** that it is crucial to have an up to date [icvpn-meta repository] to
ensure the utility outputs useful data.

The output of `findfree --help`
```
usage: findfree [-h] [-s DIRECTORY] [-p PREFIX] [-c COUNT]

Find free resources in the Freifunk ICVPN Universe

optional arguments:
  -h, --help            show this help message and exit
  -s DIRECTORY, --source-dir DIRECTORY
                        path to the local copy of the icvpn-metarepository
                        (Default: ../icvpn-meta/)
  -p PREFIX, --prefix-length PREFIX
                        Required prefix length (Default: 20)
  -c COUNT, --count COUNT
                        The amount of options to show (Default: 5)

Make sure your copy of icvpn-meta is up to date, to ensure this utility
produces useful results.
```


BGP (`mkbgp`)
-------------
`mkbgp` generates the configuration for a BGP server (currently bird and quagga
are supported) that wants to participate in the IC-VPN. It requires an already
working Layer 2 connection (Tinc, see [the icvpn repository]) and sets up BGP
sessions with other communities. This was the main reason for having the
[icvpn-meta repository] at all, to speed up the integration of new peers.

**Note** that other communities' BGP servers probably won't accept your
connection if they don't know you as a peer. It is therefore necessary to
create a suitable community file in the [icvpn-meta repository], and even then,
only communities generating their BGP communities from that repository will
accept your connection after the next update. Many communities manage their
configuration by hand, so rejected connections are not unusual.

The output of `mkbgp --help`:
```
Usage: mkbgp [options]

Options:
  -h, --help            show this help message and exit
  -f FMT, --format=FMT  Create config in format FMT.
                        Possible values: quagga, bird. Default: bird
  -4                    Generate IPv4 config
  -6                    Generate IPv6 config
  -s DIR, --sourcedir=DIR
                        Use files in DIR as input files.
                        Default: ../icvpn-meta/
  -x COMMUNITIES, --exclude=COMMUNITIES
                        Exclude the comma-separated list of COMMUNITIES
  -p PREFIX, --prefix=PREFIX
                        Prefix, e.g. bgp_icvpn_
  -P TIMEOUT, --passive-offline=TIMEOUT
                        Add peers that take longer than TIMEOUT to
                        respond at time of creation as passive peers
                        Set to 0 do disable
                        Default: 3 seconds
  -d TEMPLATE, --default=TEMPLATE
                        Default template/peer-group to use
  -t COMMUNITY:TEMPLATE, --template=COMMUNITY:TEMPLATE
                        Use different template/peer-group for some communities
```


ROA (`mkroa`)
-------------
`mkroa` creates a Route Origin Authorization (ROA) table for a bgp server
(currently only bird is supported). ROAs can be used in filters to link
prefixes to ASNs. By that, announcements are validated with the data from
the [icvpn-meta repository], so that prefixes are only imported if announced
by the correct community.

**Note** that this script does only output one ROA statement per prefix and
ASN, so you have to surround the output yourself with the appropriate table
statement, e.g. like `roa table icvpn_roa { include "roa.con?" }`.

The ROA table can then be used in a filter
```
filter icvpn_in {
  if roa_check(icvpn_roa, net, bgp_path.last) = ROA_INVALID then {
    print "ROA check failed for ", net, " ASN ", bgp_path.last;
    reject;
  }
  accept;
}
```
which then can be used e.g. in a template `import filter icvpn_in;`.

The output of `mkroa --help`:
``` 
Usage: mkroa [options]

Options:
  -h, --help            show this help message and exit
  -f FMT, --format=FMT  Create config in format FMT.
                        Possible values: bird.
  -4                    Generate IPv4 config
  -6                    Generate IPv6 config
  -s DIR, --sourcedir=DIR
                        Use files in DIR as input files.
                        Default: ../icvpn-meta/
  -x COMMUNITIES, --exclude=COMMUNITIES
                        Exclude the comma-separated list of COMMUNITIES
  -m DEFAULT_MAX_PREFIXLEN, --max=DEFAULT_MAX_PREFIXLEN
                        max prefix length to accept
```


DNS (`mkdns`)
-------------
`mkdns` generates configuration for DNS servers (currently bind and dnsmasq are
supported) to enable it to resolve the custom top level domains and reverse
`.arpa` zones of Freifunk communities by configuring the appropriate DNS
servers as forwarders for these zones.

This of course requires a working connection to the DNS servers of the
communities. While for some communities a global IPv6 connection might be
enough to reach their servers, others do not use global IPv6 and you need a
connection to the IC-VPN itself to connect (either using IPv6 or IPv4).

The output of `mkdns --help`:
```
Usage: mkdns [options]

Options:
  -h, --help            show this help message and exit
  -f FMT, --format=FMT  Create config in format FMT.
                        Possible values: bind-forward, dnsmasq, unbound, bind.
                        Default: dnsmasq
  -s DIR, --sourcedir=DIR
                        Use files in DIR as input files. Default: ../icvpn-
                        meta/
  -x COMMUNITY, --exclude=COMMUNITY
                        Exclude COMMUNITY (may be repeated)
  --filter=FILTER       Only include certain servers.
                        Possible choices: v6, v4
```


Smokeping (`mksmokeping`)
-------------------------
`mksmokeping` generates the configuration for a [Smokeping] instance to make it
monitor the BGP servers of all communities. This obviously requires a working
Layer 2 IC-VPN connection (Tinc, see [icvpn repository]), or else none of them
should be reachable..

The output of `mksmokeping --help`:
```
Usage: mksmokeping [options]

Options:
  -h, --help            show this help message and exit
  -f FMT, --format=FMT  Create config in format FMT.
                        Possible values: SmokePing. Default: SmokePing
  -s DIR, --sourcedir=DIR
                        Use files in DIR as input files.
                        Default: ../icvpn-meta/
  -x COMMUNITIES, --exclude=COMMUNITIES
                        Exclude the comma-separated list of COMMUNITIES

```

[Smokeping]: http://oss.oetiker.ch/smokeping/


Wiki ('mkwikitable')
--------------------
`mkwikitable` generates ...

The output of `mkwikitable --help`:
```
usage: mkwikitable [-h] [--meta-dir DIR]

Generate a mediawiki table about all ipv4/ipv6-networks. Uses 'api_data.dump'
generated by apireader.py, if available.

optional arguments:
  -h, --help      show this help message and exit
  --meta-dir DIR  Path to local icvpn-meta clone. Default: ../icvpn-meta/
```


Integrity checking (`check`)
----------------------------
This script checks the integrity [icvpn-meta repository]'s checkout and is used
as [its Travis CI hook](https://travis-ci.org/freifunk/icvpn-meta/). You can
use it to test your own submission to that repository beforehand, but it isn't
of much use otherwise.

Note that `check` requires Python **3.3**, for it provides an excellent
[IPv4/IPv6 manipulation
library](https://docs.python.org/3.3/library/ipaddress.html)


Visualisation (`netblocks`)
---------------------------
This script generates json-files compartible to dn42-netblock-visu to visualise
the adressspace utilisation.

The output of `netblocks --help`
```
Usage: netblocks [options]

Options:
  -h, --help            show this help message and exit
  -s DIR, --sourcedir=DIR
                        Use files in DIR as input files. Default: ../icvpn-
                        meta/
  -d DIR, --destdir=DIR
                        Use DIR as destination for the generated files.
                        Default: ./netblocks-data
```


Contributing
------------
You have an idea how to use the data in the [icvpn-meta repository]
programmatically, don't hesitate to contribute a new script. If it generates a
configuration of some kind, you might want to have a look at the `formatter`
module, which offers the `Formatter` base class that could ease the process of
config generation.

Of course, we are also happy to support more programs in the already existing
scripts!

[icvpn repository]: https://github.com/freifunk/icvpn
[icvpn-meta repository]: https://github.com/freifunk/icvpn-meta
