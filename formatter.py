from textwrap import dedent


class Formatter(object):
    """
    Abstract class to define the interface for formatters.
    """

    def __init__(self):
        """
        Initialize formatter, create initial data structures.
        Maybe determine system software versions.
        """
        self.config = []

    def populate_argument_parser(self, parser):
        """
        Populate an ArgumentParser with configuration flags.
        """
        return NotImplementedError()

    def generate_config(self, arguments, communities):
        """
        The actual work is done here.
        """
        return NotImplementedError()

    def get_config(self):
        """
        Output config string.
        """
        return "\n".join(self.config)
