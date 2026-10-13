## Level 2

Introduce operations for listing tags on parcels.

*   `list_tags(self, parcel_id: str) -> list[str]` — should return a list of all tag-value pairs for parcel `parcel_id`, sorted lexicographically by tag name. Each entry is formatted as `"tag(value)"`. Returns an empty list if the parcel does not exist.

*   `list_tags_by_prefix(self, parcel_id: str, prefix: str) -> list[str]` — should return a list of all tag-value pairs for parcel `parcel_id` where the tag starts with `prefix`, sorted lexicographically by tag name. Each entry is formatted as `"tag(value)"`. Returns an empty list if no matching tags exist.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `set_tag("parcel1", "city", "London")` | sets "city" tag |
| `set_tag("parcel1", "carrier", "FastShip")` | sets "carrier" tag |
| `set_tag("parcel1", "weight", "2kg")` | sets "weight" tag |
| `list_tags_by_prefix("parcel1", "c")` | returns ["carrier(FastShip)", "city(London)"] |
| `list_tags("parcel1")` | returns ["carrier(FastShip)", "city(London)", "weight(2kg)"] |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 6g
