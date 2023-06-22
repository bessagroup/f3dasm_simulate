from .simulator_part import ParametrizedPart


class Geometry(ParametrizedPart):
    def __init__(self, parameters=None) -> None:
        super().__init__()
