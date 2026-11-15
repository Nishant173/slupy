from bisect import bisect_left
from collections import Counter
from decimal import Decimal
import random
from typing import Any, Dict, List, Union

from slupy.core.helpers import create_repr, get_num_decimal_places


def validate_distribution(distribution: Any) -> None:
    """Raises error if the given distribution is invalid."""
    if not isinstance(distribution, dict):
        raise TypeError("Distribution must be of type dict")
    if not distribution:
        raise ValueError("Distribution must be non-empty")

    dist_pct = Decimal("0.0")
    for key, value in distribution.items():
        if not isinstance(key, str) or not key:
            raise ValueError("Distribution keys must be non-empty strings")
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not (0 < value <= 100)
            or get_num_decimal_places(float(value)) > 3
        ):
            raise ValueError(
                "Distribution values must be int|float between (0, 100]."
                " They can have up to 3 decimal places."
                f" Got value {value!r} of type {type(value).__name__}."
            )
        dist_pct += Decimal(str(value))

    if dist_pct != Decimal("100"):
        raise ValueError(f"Sum of distribution values must be 100, but got {dist_pct}")


class BaseDistribution:
    """Base class for category distributions."""

    def __init__(
            self,
            *,
            distribution: Dict[str, Union[int, float]],
        ) -> None:
        validate_distribution(distribution)
        self.distribution: Dict[str, Union[int, float]] = dict(distribution)
        self.sample_size: int = 10 ** (2 + self.compute_max_decimal_places())
        self.limits: Dict[str, int] = {}
        self.cumulative_limits: Dict[str, int] = {}
        self._compute_and_set_limits()

    def __str__(self) -> str:
        return create_repr(
            instance=self,
            kwargs_dict={
                "distribution": self.distribution,
                "sample_size": self.sample_size,
                "limits": self.limits,
                "cumulative_limits": self.cumulative_limits,
            },
            multi_line=True,
        )

    def compute_max_decimal_places(self) -> int:
        return max(
            get_num_decimal_places(float(pct))
            for pct in self.distribution.values()
        )

    def _compute_and_set_limits(self) -> None:
        cumulative = 0
        for category, pct in self.distribution.items():
            # Use Decimal arithmetic to avoid float rounding issues
            limit = int((Decimal(str(pct)) / Decimal("100")) * self.sample_size)
            cumulative += limit
            self.limits[category] = limit
            self.cumulative_limits[category] = cumulative

    def compute_category(self) -> str:
        raise NotImplementedError()

    def get_category_counter_for_sample_size(self) -> Counter[str]:
        return Counter(self.compute_category() for _ in range(self.sample_size))


class RandomDistribution(BaseDistribution):
    """Distributes categories randomly according to weights."""

    def __init__(self, *, distribution: Dict[str, Union[int, float]]) -> None:
        super().__init__(distribution=distribution)
        self._categories: List[str] = list(self.cumulative_limits.keys())
        self._cum_weights: List[int] = list(self.cumulative_limits.values())

    def compute_category(self) -> str:
        random_int = random.randint(1, self.sample_size)
        idx = bisect_left(self._cum_weights, random_int)
        return self._categories[idx]


class ExactDistribution(BaseDistribution):
    """Distributes categories to 100% exact proportions per sample_size cycle."""

    def __init__(
            self,
            *,
            distribution: Dict[str, Union[int, float]],
            shuffle: bool = True,
        ) -> None:
        super().__init__(distribution=distribution)
        self.shuffle = shuffle
        self._pool: List[str] = []

    def _refill_pool(self) -> None:
        self._pool = [
            category
            for category, count in self.limits.items()
            for _ in range(count)
        ]
        if self.shuffle:
            random.shuffle(self._pool)

    def compute_category(self) -> str:
        if not self._pool:
            self._refill_pool()
        return self._pool.pop()

