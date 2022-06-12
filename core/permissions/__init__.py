from .legacy import IsStaffOrReadOnly
from .hybrid import (
    IsStaffOrReadOnlyOrTokenHasScope,
    IsStaffOrTokenHasScope,
    IsStaffOrTokenMatchesOASRequirements,
    IsStaffOrReadOnlyTokenMatchesOASRequirements,
)
