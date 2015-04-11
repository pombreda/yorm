"""Base class for mapped objects."""

import abc

from .. import common

log = common.logger(__name__)


MAPPER = 'yorm_mapper'


class Mappable(metaclass=abc.ABCMeta):

    """Base class for objects with attributes mapped to file."""

    def __getattribute__(self, name):
        if name == MAPPER:
            # avoid infinite recursion (attribute requested in this function)
            return object.__getattribute__(self, name)
        mapper = getattr(self, MAPPER, None)

        # Get the attribute's current value
        try:
            value = object.__getattribute__(self, name)
        except AttributeError as exc:
            missing = True
            if not mapper:
                raise exc from None
        else:
            missing = False

        # Fetch a new value from disk if the attribute is mapped or missing
        if mapper and (missing or name in mapper.attrs):
            mapper.fetch()
            value = object.__getattribute__(self, name)

        return value

    def __setattr__(self, name, value):
        mapper = getattr(self, MAPPER, None)

        # Convert the value to the mapped type
        if mapper and name in mapper.attrs:
            converter = mapper.attrs[name]
            value = converter.to_value(value)

        # Set the attribute's new value
        object.__setattr__(self, name, value)

        # Store the attribute to disk
        if mapper and mapper.auto and name in mapper.attrs:
            self.yorm_mapper.store()