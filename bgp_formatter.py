from argparse import ArgumentParser
from collections import defaultdict
from textwrap import dedent

from formatter import Formatter


class _BGPFormatter(Formatter):
    "Basic Formatter for BGP configurations"

    def populate_argument_parser(self, parser):
        parser.add_argument("-4",
                            dest="family",
                            action="store_const",
                            const="ipv4",
                            help="Generate IPv4 config")
        parser.add_argument("-6",
                            dest="family",
                            action="store_const",
                            const="ipv6",
                            help="Generate IPv6 config")
        parser.add_argument("-p", "--prefix", dest="prefix",
                            help="Prefix for protocol names, e.g. bgp_icvpn_<community>",
                            metavar="PREFIX",
                            default="")
        parser.add_argument("-d", "--default",
                            dest="defaulttemplate",
                            help="Default template/peer-group to use",
                            metavar="TEMPLATE",
                            default=None)
        parser.add_argument("-t", "--template",
                            dest="templates",
                            action="append",
                            help="Define protocol template/peer-group" +
                                 "for community",
                            metavar="COMMUNITY:TEMPLATE",
                            default=[])
        parser.set_defaults(family="ipv6")

    def generate_config(self, arguments, communities):

        template = defaultdict(lambda: arguments.defaulttemplate)
        template.update(dict(map(lambda s: s.split(":"), arguments.templates)))

        family = arguments.family

        for community, data in communities:
            try:
                bgp = data["bgp"]
                asn = data["asn"]
            except (TypeError, KeyError):
                continue

            for host in sorted(bgp.keys()):
                d = bgp[host]
                if family not in d:
                    continue

                peer = d[family]
                self.config.append(
                    dedent(self.config_template %
                           {"prefix": arguments.prefix + host,
                            "template": template[community],
                            "peer": peer,
                            "asn": asn}))


class BirdFormatter(_BGPFormatter):
    "Formatter for bind9 using type forward"

    config_template = """
            protocol bgp %(prefix)s from %(template)s {
                neighbor %(peer)s as %(asn)s;
            }
        """


class QuaggaFormatter(_BGPFormatter):
    "Formatter for quagga"

    config_template = """
            neighbor %(peer)s remote-as %(asn)s
            neighbor %(peer)s description %(prefix)s
            neighbor %(peer)s peer-group %(template)s
        """
