## Level 3

Introduce timestamped tag operations, allowing tags to be set at a specific timestamp and optionally expire after a TTL. It is guaranteed that the `timestamp` argument is non-decreasing across all operations from Level 3 onward, and that `ttl` is never negative.

*   `set_tag_at(self, parcel_id: str, tag: str, value: str, timestamp: int) -> None` — should set or overwrite the `tag` to `value` for parcel `parcel_id` at the given `timestamp`. A tag set with `set_tag_at` does not expire unless overwritten.

*   `get_tag_at(self, parcel_id: str, tag: str, timestamp: int) -> str | None` — should return the value of `tag` for parcel `parcel_id` as it was at `timestamp`. Returns `None` if the tag did not exist or had expired at `timestamp`.

*   `remove_tag_at(self, parcel_id: str, tag: str, timestamp: int) -> bool` — should remove the `tag` from parcel `parcel_id` only if the tag is currently valid at `timestamp`, i.e. it exists and has not yet expired at that time (using the same exclusive expiry boundary as `get_tag_at`: a tag expiring at `timestamp` is already considered expired). Returns `True` if the tag was removed this way. Returns `False` if the parcel does not exist, the tag was never set on it, the tag was already removed, or the tag had already expired by `timestamp`.

*   `set_tag_with_hold(self, parcel_id: str, tag: str, value: str, timestamp: int, ttl: int) -> None` — should set or overwrite the `tag` to `value` for parcel `parcel_id` at `timestamp`, with a time-to-live of `ttl` milliseconds. The tag expires at `timestamp + ttl`. If `ttl` is `0`, the tag does not expire.

*   `list_tags_at(self, parcel_id: str, timestamp: int) -> list[str]` — should return a list of all tag-value pairs for parcel `parcel_id` that were valid at `timestamp`, sorted lexicographically by tag name. Each entry is formatted as `"tag(value)"`.

*   `list_tags_by_prefix_at(self, parcel_id: str, prefix: str, timestamp: int) -> list[str]` — should return a list of all tag-value pairs for parcel `parcel_id` where the tag starts with `prefix` and was valid at `timestamp`, sorted lexicographically by tag name. Each entry is formatted as `"tag(value)"`.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `set_tag_with_hold("parcel1", "status", "held", 100, 50)` | sets "status" to "held" at ts=100, expires after 50 (at 150) |
| `get_tag_at("parcel1", "status", 120)` | returns "held"; valid at 120 |
| `get_tag_at("parcel1", "status", 150)` | returns None; expired at 150 |
| `get_tag_at("parcel1", "status", 180)` | returns None; still expired |

Example demonstrating `remove_tag_at`:

| Queries | Explanations |
| --- | --- |
| `set_tag_with_hold("parcel2", "status", "held", 200, 40)` | sets "status" to "held" at ts=200, expires at 240 |
| `set_tag_at("parcel2", "fragile", "yes", 210)` | sets "fragile"; never expires |
| `remove_tag_at("parcel2", "fragile", 220)` | returns True; valid at 220, removed |
| `remove_tag_at("parcel2", "fragile", 225)` | returns False; already removed |
| `remove_tag_at("parcel2", "status", 240)` | returns False; a tag expiring at 240 is already expired |
| `list_tags_at("parcel2", 240)` | returns []; nothing left |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 6g
