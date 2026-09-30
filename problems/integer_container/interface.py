from __future__ import annotations

from abc import ABC


class IntegerContainer(ABC):
    """
    `IntegerContainer` interface.
    Default implementations return placeholder values; override every method
    in `IntegerContainerImpl` (integer_container_impl.py).
    """

# @@LEVEL 1@@
    def add(self, value: int) -> int:
        """
        Should add the specified integer `value` to the container and return
        the number of integers in the container after the addition.
        """
        # default implementation
        return 0

    def delete(self, value: int) -> bool:
        """
        Should attempt to remove one occurrence of `value` from the container.
        If present, remove it and return `True`; otherwise return `False`.
        """
        # default implementation
        return False

# @@LEVEL 2@@
    def get_median(self) -> int | None:
        """
        Should return the middle integer of the sorted sequence of all stored
        integers. For an even count, return the leftmost of the two middle
        integers. Return `None` if the container is empty.
        """
        # default implementation
        return None

# @@LEVEL 3@@
    def count_in_range(self, low: int, high: int) -> int:
        """
        Should return how many stored integers v satisfy low <= v <= high.
        Return 0 if low > high.
        """
        # default implementation
        return 0

    def get_kth_smallest(self, k: int) -> int | None:
        """
        Should return the k-th smallest stored integer (1-based).
        Return `None` if k < 1 or k > number of stored integers.
        """
        # default implementation
        return None

# @@LEVEL 4@@
    def undo(self) -> bool:
        """
        Should revert the most recent successful `add`/`delete` not yet undone.
        Return `True` if something was undone, `False` otherwise.
        """
        # default implementation
        return False

    def redo(self) -> bool:
        """
        Should re-apply the most recently undone change.
        Return `True` if something was redone, `False` otherwise.
        """
        # default implementation
        return False
