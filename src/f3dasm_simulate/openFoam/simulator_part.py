"""
SimulatorPart is a protocol that defines the interface for a simulator part.
"""

#                                                                       Modules
# =============================================================================

from typing import Protocol, runtime_checkable

#                                                        Authorship and Credits
# =============================================================================
__author__ = "Jiaxiang Yi (J.Yi@tudelft.nl), Martin van der Schelling (M.P.vanderSchelling@tudelft.nl)"
__credits__ = ["Martin van der Schelling", "Jiaxiang Yi"]
__status__ = "Stable"
# =============================================================================
#
# =============================================================================


@runtime_checkable
class SimulatorPart(Protocol):
    @classmethod
    def from_dict(cls, dict_: dict) -> "SimulatorPart":
        # check if the keys of dict_ are the same as the attributes of the class
        assert set(dict_.keys()).issubset(set(cls.__init__.__annotations__.keys())), (
            f"dict_ keys {set(dict_.keys())} should be keys of "
            + f"the attributes of the {cls.__name__} class: {set(cls.__init__.__annotations__.keys())}"
        )

        # check if the values of dict_ are the same type as the attributes of the class
        for key, value in dict_.items():
            assert isinstance(value, cls.__init__.__annotations__[key]), (
                f"argument {key} with type {type(value)} should be the same "
                + f"type as the attribute {key} of the {cls.__name__} class: "
                + f"{cls.__init__.__annotations__[key]}"
            )

        return cls(**dict_)

    def to_dict(self) -> dict:
        """
        Recursively traverse the attributes and return a flat dict representation.
        """
        sim_info = {}
        for k, v in self.__dict__.items():
            if isinstance(v, SimulatorPart):
                sim_info.update(v.to_dict())
            else:
                sim_info[k] = v

        return sim_info

    def get_structured_parameters(self) -> dict:
        struct_parameters = {}
        for k, v in self.__dict__.items():
            if isinstance(v, ParametrizedPart):
                struct_parameters[k] = dict(description=v.description, values=v.values)

        return struct_parameters


class ParametrizedPart(SimulatorPart):
    def __init__(self, description="parameters", parameters=None) -> None:
        self.description = description
        self.values = {}
        if parameters:
            for k, v in parameters.items():
                try:
                    self.values[k] = {
                        "default": v["value"],
                        "description": v["description"],
                    }

                except KeyError as e:
                    print("A parameter should contain a description and a value.")
