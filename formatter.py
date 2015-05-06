from textwrap import dedent


class Formatter(object):
    """
    Abstract class to define the interface for formatters.
    """

    comment_prefix = '#'

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

    def add_comment(self, comment):
        """
        Add a comment to the config.
        """
        self.config.append(self.comment_prefix + ("\n%s " % self.comment_prefix).join(dedent(comment).split("\n")))

    def get_config(self):
        """
        Output config string.
        """
        return "\n".join(self.config)
