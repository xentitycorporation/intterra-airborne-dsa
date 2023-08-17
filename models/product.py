from datetime import datetime


class Product:
    def __init__(self, type: str, subtype: str | None, timestamp: datetime) -> None:
        if type not in ["image", "tactical", "video"]:
            raise ValueError(f"Invalid product type: {type}]")
        self._type = type

        if type == "image":
            if subtype not in ["EO", "HS", "IR"]:
                raise ValueError(f"Invalid image product subtype: {subtype}]")
        elif type == "tactical":
            if subtype not in [
                "Detection",
                "DPS",
                "HeatPerimeter",
                "IntenseHeat",
                "IsolatedHeat",
                "ScatteredHeat",
            ]:
                raise ValueError(f"Invalid tactical product subtype: {subtype}]")
        self._subtype = subtype

        self._timestamp = timestamp

    @property
    def type(self) -> str:
        """Product type"""
        return self._type

    @property
    def subtype(self) -> str | None:
        """Product subtype"""
        return self._subtype

    @property
    def timestamp(self) -> datetime:
        """Product timestamp"""
        return self._timestamp

    def __str__(self) -> str:
        return f"Product(type='{self._type}', subtype='{self._subtype}', timestamp='{self._timestamp}'])"

    def __eq__(self, __value: object) -> bool:
        return (
            isinstance(__value, Product)
            and self._type == __value.type
            and self._subtype == __value.subtype
            and self._timestamp == __value.timestamp
        )
