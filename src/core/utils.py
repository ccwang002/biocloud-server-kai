from collections import OrderedDict
import enum
import importlib
import yaml

def str_to_class(module_name, class_name):
    """
    Mimic ``from module import class``.
    Adapted from http://stackoverflow.com/a/24674853

    Args:
        module_name (str): name of the module
        class_name (str): name of the class

    Returns:
        Imported class
    """
    try:
        module_ = importlib.import_module(module_name)
        try:
            class_ = getattr(module_, class_name)()
        except AttributeError as e:
            raise AttributeError(
                'Class %s does not exist in module %s' % (
                    class_name, module_name
                )
            ) from e
    except ImportError as e:
        raise ImportError('Module %s does not exist' % module_name) from e
    return class_


class ChoiceEnum(enum.Enum):

    @classmethod
    def choices(cls):
        return [
            (member_name, member.value)
            for member_name, member in cls.__members__.items()
        ]

    @classmethod
    def from_choice(cls, choice):
        try:
            return cls.__members__[choice]
        except KeyError as e:
            raise ValueError(
                '%(cls)s does not have the given choice %(choice)r.' % {
                    'cls': cls.__name__,
                    'choice': choice,
                }
            ) from e


class ValueDescriptionChoiceEnum(ChoiceEnum):

    def __init__(self, verbose_name, description):
        self.verbose_name = verbose_name
        self.description = description

    @classmethod
    def choices(cls):
        return [
            (member_name, member.verbose_name)
            for member_name, member in cls.__members__.items()
        ]



# Set up PyYAML
# Ref: https://stackoverflow.com/a/31609484
def setup_yaml():
    """ https://stackoverflow.com/a/8661021 """
    def represent_dict_order(dumper, data):
        return dumper.represent_mapping(
            'tag:yaml.org,2002:map', data.items(), flow_style=False
        )

    yaml.add_representer(OrderedDict, represent_dict_order)
