from __future__ import annotations

from typing import Any, Callable, Dict, List, Literal, Optional

from slupy.core import checks
from slupy.core.helpers import make_deep_copy


class DataWrangler:
    """Class that represents a data wrangler"""

    def __init__(
            self,
            list_of_dicts: List[Dict[str, Any]],
            /,
            *,
            deep_copy: Optional[bool] = False,
        ) -> None:
        """
        Parameters:
            - list_of_dicts (list): List of dictionaries.
            - deep_copy (bool): If `deep_copy=True`, creates a deep-copy of the given `list_of_dicts` and
            ensures that the original is never modified.
        """
        self._list_of_dicts = make_deep_copy(list_of_dicts) if deep_copy else list_of_dicts

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        return self.data[idx]

    def copy(self) -> DataWrangler:
        """Returns deep-copy of `self`"""
        return make_deep_copy(self)

    @property
    def data(self) -> List[Dict[str, Any]]:
        return self._list_of_dicts

    @data.setter
    def data(self, value: List[Dict[str, Any]]) -> None:
        self._list_of_dicts = value

    def data_copy(self) -> List[Dict[str, Any]]:
        """Returns deep-copy of `self.data`"""
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
        for idx, dict_obj in enumerate(self.data):
            if idx in indices_involved_in_duplicates:
                continue
            sub_indices = []
            list_remainder = self.data[idx + 1 : ]
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
        """Compares the given 2 dictionaries based on the subset of keys"""
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
            inplace: Optional[bool] = False,
        ) -> DataWrangler:
        """Drops the duplicate rows"""
        list_obj = self.data if inplace else self.data_copy()
        indices = self._identify_duplicate_indices(subset=subset)
        if not indices:
            return self if inplace else DataWrangler(list_obj)
        indices_to_drop = []
        for sub_indices in indices:
            if keep == "first":
                temp = list(set(sub_indices).difference(set([min(sub_indices)])))
                indices_to_drop.extend(temp)
            elif keep == "last":
                temp = list(set(sub_indices).difference(set([max(sub_indices)])))
                indices_to_drop.extend(temp)
        for idx in sorted(indices_to_drop, reverse=True):
            list_obj.pop(idx)
        return self if inplace else DataWrangler(list_obj)

    def get_values_by_field(self, *, field: str) -> List[Any]:
        """Returns a list of values for the given field"""
        values = []
        for idx, dict_obj in enumerate(self.data):
            try:
                value = dict_obj[field]
            except KeyError:
                raise KeyError(f"Field '{field}' is not found on row number {idx + 1}")
            values.append(value)
        return values

    def get_unique_fields(self) -> List[str]:
        """Returns list of all the unique fields that are present"""
        unique_fields = set()
        for dict_obj in self.data:
            unique_fields = unique_fields.union(set(dict_obj.keys()))
        return list(sorted(unique_fields, reverse=False))

    def set_defaults_for_fields(
            self,
            *,
            fields: List[str],
            inplace: Optional[bool] = False,
        ) -> DataWrangler:
        """
        Checks if the given fields are present in each dictionary in the list.
        If not present, sets their default value to `None`.
        """
        assert checks.is_list_of_instances_of_type(fields, type_=str, allow_empty=False), (
            "Param `fields` must be a non-empty list of strings"
        )
        list_obj = self.data if inplace else self.data_copy()
        for dict_obj in list_obj:
            for field in fields:
                dict_obj.setdefault(field, None)
        return self if inplace else DataWrangler(list_obj)

    def compute_field(
            self,
            *,
            field: str,
            func: Callable[[Dict[str, Any]], Any],
            inplace: Optional[bool] = False,
        ) -> DataWrangler:
        """
        Applies the given function `func` to each dictionary in the list, and stores the result of `func` in the key `field` of each dictionary.
        The `func` takes in the dictionary (row) as a parameter.
        """
        list_obj = self.data if inplace else self.data_copy()
        for dict_obj in list_obj:
            computed_value = func(dict_obj)
            dict_obj[field] = computed_value
        return self if inplace else DataWrangler(list_obj)

    def drop_fields(
            self,
            *,
            fields: List[str],
            inplace: Optional[bool] = False,
        ) -> DataWrangler:
        """Drops the given fields"""
        assert checks.is_list_of_instances_of_type(fields, type_=str, allow_empty=False), (
            "Param `fields` must be a non-empty list of strings"
        )
        list_obj = self.data if inplace else self.data_copy()
        for dict_obj in list_obj:
            for field in fields:
                dict_obj.pop(field, None)
        return self if inplace else DataWrangler(list_obj)

    def fill_nulls(
            self,
            *,
            value: Any,
            subset: Optional[List[str]] = None,
            inplace: Optional[bool] = False,
        ) -> DataWrangler:
        """Fills all values that are `None` with `value`"""
        list_obj = self.data if inplace else self.data_copy()
        for dict_obj in list_obj:
            keys = subset if subset else list(dict_obj.keys())
            for key in keys:
                try:
                    existing_value = dict_obj[key]
                except KeyError:
                    raise KeyError(f"Key '{key}' from subset is not found")
                if existing_value is None:
                    dict_obj[key] = value
        return self if inplace else DataWrangler(list_obj)

    def filter_rows(
            self,
            *,
            func: Callable[[Dict[str, Any]], bool],
            inplace: Optional[bool] = False,
        ) -> DataWrangler:
        """
        Applies the given function `func` to each dictionary (row) in the list, and expects the `func` to return a boolean.
        If the result is `True` then keeps the row; otherwise removes the row.
        The `func` takes in the dictionary (row) as a parameter.
        """
        list_obj = self.data if inplace else self.data_copy()
        list_obj_filtered: List[Dict[str, Any]] = []
        for dict_obj in list_obj:
            should_keep_row: bool = func(dict_obj)
            assert isinstance(should_keep_row, bool), f"Result of `func` must be of type boolean"
            if should_keep_row:
                list_obj_filtered.append(dict_obj)

        if inplace:
            self.data = list_obj_filtered
        else:
            list_obj = list_obj_filtered

        return self if inplace else DataWrangler(list_obj)

