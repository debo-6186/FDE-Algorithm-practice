## Level 4

Introduce checkpoints that save and restore the state of all parcels.

*   `checkpoint(self, timestamp: int) -> int` — should create a checkpoint of the current state of all parcels at `timestamp`. Returns the number of parcels that are currently alive (have at least one valid tag) at `timestamp`.

*   `restore_checkpoint(self, timestamp: int, timestamp_to_restore: int) -> None` — should restore the state of all parcels to the latest checkpoint at or before `timestamp_to_restore`. That checkpoint's own timestamp (call it `checkpoint_timestamp`) may be earlier than `timestamp_to_restore` if no checkpoint was taken exactly at that time; only checkpoints at or before `timestamp_to_restore` are considered. After restoring, any tags added or removed after `checkpoint_timestamp` are rolled back. Every restored tag that has a finite expiration is shifted forward by `timestamp - checkpoint_timestamp`, so its new expiration becomes `original_expiration + (timestamp - checkpoint_timestamp)`; tags that were set without a TTL keep no expiration. If no checkpoint exists at or before `timestamp_to_restore`, this operation has no effect. It is guaranteed that `timestamp_to_restore` never exceeds `timestamp`.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `set_tag_with_hold("parcel1", "status", "held", 100, 100)` | sets "status" to "held" at ts=100, expires after 100 (at 200) |
| `checkpoint(120)` | returns 1; 1 parcel alive at ts=120 |
| `checkpoint(150)` | returns 1; 1 parcel alive at ts=150 (set at 100, not yet expired) |
| `checkpoint(200)` | returns 0; expired at 200 |
| `restore_checkpoint(250, 120)` | restores to state at ts=120 (before expiry); delta = 250 - 120 = 130, so "status" now expires at 200 + 130 = 330 |
| `get_tag_at("parcel1", "status", 300)` | returns "held"; restored, and 300 < 330 |

Example demonstrating that the expiration shift is based on the actual checkpoint's timestamp, not `timestamp_to_restore`:

| Queries | Explanations |
| --- | --- |
| `set_tag_with_hold("parcel1", "route_east", "active", 30, 70)` | sets "route_east" to "active" at ts=30, expires after 70 (at 100) |
| `checkpoint(31)` | checkpoint taken at ts=31 with "route_east" alive |
| `set_tag_with_hold("parcel1", "route_west", "queued", 35, 25)` | sets "route_west" to "queued" at ts=35, expires after 25 (at 60) |
| `checkpoint(41)` | checkpoint taken at ts=41 with "route_east" and "route_west" alive |
| `restore_checkpoint(110, 35)` | restores to the checkpoint at ts=31 (the latest one at or before 35, not 35 itself); delta = 110 - 31 = 79 |
| `get_tag_at("parcel1", "route_west", 115)` | returns None; "route_west" did not exist yet in the ts=31 checkpoint, so it is discarded |
| `get_tag_at("parcel1", "route_east", 115)` | returns "active"; "route_east"'s expiration shifts by delta to 100 + 79 = 179, so it is still valid at ts=115 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 6g
