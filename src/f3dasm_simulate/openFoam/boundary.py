from .simulator_part import ParametrizedPart


class Boundary(ParametrizedPart):
    def __init__(self, parameters=None) -> None:
        super().__init__(parameters=parameters)
