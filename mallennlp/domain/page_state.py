from typing import Dict, List

import attr
from mallennlp.domain.storable import Storable


@attr.s
class PageSessionState(Storable):
    @classmethod
    def from_params(cls, params: Dict[str, List[str]]):
        return cls()
