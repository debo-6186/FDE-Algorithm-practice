## Level 1

The basic level of the parcel tracking system contains parcels. Each parcel is accessed with a unique identifier `parcel_id` of *string* type. A parcel contains several `tag` - `value` pairs, where both `tag` and `value` are *strings*.

*   `set_tag(self, parcel_id: str, tag: str, value: str) -> None` — should set or overwrite the `tag` to `value` for the parcel identified by `parcel_id`.

*   `get_tag(self, parcel_id: str, tag: str) -> str | None` — should return the value of `tag` for the parcel identified by `parcel_id`. If the parcel or tag does not exist, should return `None`.

*   `remove_tag(self, parcel_id: str, tag: str) -> bool` — should remove the `tag` from parcel `parcel_id`. Returns `True` if the tag was removed or `False` if the tag did not exist.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `set_tag("parcel1", "status", "in-transit")` | sets tag "status" to "in-transit" |
| `get_tag("parcel1", "status")` | returns "in-transit" |
| `set_tag("parcel1", "status", "delivered")` | overwrites "status" to "delivered" |
| `get_tag("parcel1", "status")` | returns "delivered" |
| `remove_tag("parcel1", "status")` | returns True; tag removed |
| `get_tag("parcel1", "status")` | returns None; tag no longer exists |
| `remove_tag("parcel1", "status")` | returns False; tag already removed |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 6g
