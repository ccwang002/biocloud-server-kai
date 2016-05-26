import enum


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
