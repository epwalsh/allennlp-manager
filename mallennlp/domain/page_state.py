from typing import Dict, List, Any

import attr


@attr.s(kw_only=True)
class BasePageState:
    @classmethod
    def from_params(cls, params: Dict[str, List[str]]):
        return cls()

    @classmethod
    def from_store(cls, data: Dict[str, Any]):
        return cls(**data)  # type: ignore

    def dump_store(self) -> Dict[str, Any]:
        return attr.asdict(self)
