from formatter import Formatter
from textwrap import dedent


class SmokePingFormatter(Formatter):
    "Formatter for SmokePing (http://oss.oetiker.ch/smokeping/)"

    def populate_argument_parser(self, parser):
        pass

    def generate_config(self, arguments, communities):

        host_probe = """
            ++ %(name)s
            menu = %(name)s
            title = %(name)s
            probe = %(probe)s
            host = %(ip)s
            #alerts = someloss

            """

        community_section = """
            + %(name)s
            menu = %(name)s
            title = %(name)s

            """

        for community, data in communities:

            try:
                bgp = data["bgp"]
            except (TypeError, KeyError):
                continue

            self.config.append(dedent(
                community_section % {"name": community}))

            for host in sorted(bgp.keys()):
                d = bgp[host]
                if 'ipv4' in d:
                    peer = d['ipv4']
                    self.config.append(dedent(
                        host_probe %
                        {"name": "ipv4-{}".format(host), "ip": peer, "probe": "FPing"}))
                if 'ipv6' in d:
                    peer = d['ipv6']
                    self.config.append(dedent(
                        host_probe %
                        {"name": "ipv6-{}".format(host), "ip": peer, "probe": "FPing6"}))
