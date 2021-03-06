from collections import OrderedDict, defaultdict

from django.utils.functional import cached_property
from django.utils.html import mark_safe


class ToolSpec:
    def __init__(
        self, name, version_string, description='', url='',
    ):
        """Specification to define a tool used in any analysis.

        Args:
            name (str): Tool's name

            version_string (str):
                Tool's version.
                Ex. 0.2.4, 3.0. Don't prefix it with "v".

            description (str): Description about what this tool does.

            url (str):
                URL to the tool's project website.
                Ex. http://www.google.com/
        """
        self.name = name
        self.version = version_string
        self.description = description
        self.url = url
        if len(self.db_name) > 128:
            raise ValueError(
                "Either tool name or the version string is too long. "
                "Combined db name {} must short than 128 chars."
                .format(self.db_name)
            )

    @property
    def db_name(self):
        return "%s_%s" % (self.name, self.version)

    def as_link(self):
        """Format as a HTML link element."""
        return mark_safe(
            '<a href="{url:s}" target="_blank">{name:s}</a>'
            .format(url=self.url, name=self.name)
        )

    def __str__(self):
        return "{name:s} v{ver:s}".format(
            name=self.name, ver=self.version
        )

    def __repr__(self):
        return "<{cls_name:s}: {str_val:s}>".format(
            cls_name=self.__class__.__name__,
            str_val=str(self),
        )

    __slots__ = [
        "name", "version", "description", "url",
    ]


class ToolSet:
    def __init__(self, toolspecs):
        self.tools = OrderedDict()
        self.general_tools = defaultdict(list)
        for toolspec in toolspecs:
            self.add_tool(toolspec)

    def add_tool(self, toolspec):
        """Add a new tool into current toolset.

        Args:
            toolspec (ToolSpec):
        """
        if not isinstance(toolspec, ToolSpec):
            raise ValueError(
                "Can only add ToolSpec object into toolset. "
                "%s is not a ToolSpec." % toolspec
            )
        if toolspec.db_name in self.tools:
            raise ValueError(
                "ToolSpec {toolspec!s} already exists in this toolset"
                .format(toolspec=toolspec)
            )
        self.tools[toolspec.db_name] = toolspec
        self.general_tools[toolspec.name].append(toolspec)

    @cached_property
    def db_choices(self):
        return [
            (db_name, str(toolspec))
            for db_name, toolspec in self.tools.items()
        ]

    @cached_property
    def each_per_name(self):
        return {
            name: toolspecs[0]
            for name, toolspecs in self.general_tools.items()
        }

    def subset(self, tool_names):
        """Return a new ToolSet leaving only tools within tool_names.

        """
        toolspecs = []
        for name in tool_names:
            toolspecs.extend(self.general_tools[name])
        return ToolSet(toolspecs)
