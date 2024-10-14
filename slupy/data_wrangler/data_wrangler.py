from __future__ import annotations

from typing import Any, Callable, Dict, List, Literal, Optional

from slupy.core.helpers import make_deep_copy


class DataWrangler:
    """Class that represents a data wrangler"""

    def __init__(
            self,
            list_of_dicts: List[Dict[str, Any]],
            /,
        ) -> None:
        self._list_of_dicts = list_of_dicts

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def copy(self) -> DataWrangler:
        """Returns deep-copy of `self`"""
        return make_deep_copy(self)

    @property
    def data(self) -> List[Dict[str, Any]]:
        return self._list_of_dicts

    def data_copy(self) -> List[Dict[str, Any]]:
        """Returns deep-copy of `self._list_of_dicts`"""
        return make_deep_copy(self._list_of_dicts)

    def _identify_duplicate_indices(
            self,
            *,
            break_at: Optional[Literal["first", "first_full"]] = None,
            subset: Optional[List[str]] = None,
        ) -> List[List[int]]:
        """
        Returns list of list of indices that correspond to duplicates. If no duplicates are found, returns an empty list.
        Eg: An output of `[[0, 4, 5], [1, 6, 8]]` means that dictionaries at indices (0, 4, 5) are duplicates of the same
        value; and dictionaries at indices (1, 6, 8) are duplicates of the same value.

        Parameters:
            - break_at (str): If `break_at='first'`, returns early with the first 2 indices of the first set of duplicates identified (if any).
            If `break_at='first_full'`, returns early with all the indices of the first set of duplicates identified (if any).
            - subset (List[str]): List of keys to consider in each dictionary in the list.
        """
        indices = []
        indices_involved_in_duplicates = set()
        for idx, dict_obj in enumerate(self._list_of_dicts):
            if idx in indices_involved_in_duplicates:
                continue
            sub_indices = []
            list_remainder = self._list_of_dicts[idx + 1 : ]
            for idx_inner, dict_obj_inner in enumerate(list_remainder):
                overall_idx = idx + idx_inner + 1
                if self._is_equal(dict_obj, dict_obj_inner, subset=subset):
                    indices_involved_in_duplicates.add(idx)
                    indices_involved_in_duplicates.add(overall_idx)
                    if not sub_indices:
                        sub_indices.append(idx)
                    sub_indices.append(overall_idx)
                    if break_at == "first":
                        return [sub_indices]
            if sub_indices:
                indices.append(sub_indices)
                if break_at == "first_full":
                    return indices
        return indices

    def _is_equal(
            self,
            d1: Dict[str, Any],
            d2: Dict[str, Any],
            /,
            *,
            subset: Optional[List[str]] = None,
        ) -> bool:
        if not subset:
            return d1 == d2
        for key in subset:
            try:
                are_equal: bool = d1[key] == d2[key]
            except KeyError:
                raise KeyError(f"Key '{key}' from subset is not found")
            if not are_equal:
                return False
        return True

    def has_duplicates(
            self,
            *,
            subset: Optional[List[str]] = None,
        ) -> bool:
        return bool(
            self._identify_duplicate_indices(break_at="first", subset=subset)
        )

    def drop_duplicates(
            self,
            *,
            keep: Optional[Literal["first", "last"]] = "first",
            subset: Optional[List[str]] = None,
        ) -> List[Dict[str, Any]]:
        """Returns new copy of list of dictionaries with the duplicates dropped"""
        list_copy = self.data_copy()
        indices = self._identify_duplicate_indices(subset=subset)
        if not indices:
            return list_copy
        indices_to_drop = []
        for sub_indices in indices:
            if keep == "first":
                temp = list(set(sub_indices).difference(set([min(sub_indices)])))
                indices_to_drop.extend(temp)
            elif keep == "last":
                temp = list(set(sub_indices).difference(set([max(sub_indices)])))
                indices_to_drop.extend(temp)
        for idx in sorted(indices_to_drop, reverse=True):
            list_copy.pop(idx)
        return list_copy

    def apply(self, *, func: Callable) -> List[Any]:
        """Applies the given function (`func`) to each dictionary in the list"""
        return [
            func(item) for item in self.data_copy()
        ]

    def apply_to_field(self, *, field: str, func: Callable) -> List[Any]:
        """Applies the given function (`func`) to the field (`field`) in each dictionary in the list"""
        result = self.data_copy()
        for idx, item in enumerate(result):
            try:
                value = item[field]
            except KeyError:
                raise KeyError(f"Field '{field}' not found on row number {idx + 1}")
            new_value = func(value)
            item[field] = new_value
        return result

