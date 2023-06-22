from .simulator_part import ParametrizedPart


class Material(ParametrizedPart):
    def __init__(self, parameters=None) -> None:
        super().__init__(parameters=parameters)
