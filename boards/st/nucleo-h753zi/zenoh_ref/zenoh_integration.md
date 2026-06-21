# Zenoh Implementation and Integration — ST Nucleo-H753ZI

This document covers the internal implementation of PX4's Zenoh module and the
complete step-by-step workflow for enabling Zenoh on the ST Nucleo-H753ZI board.

---

## 1. Introduction

PX4's Zenoh support replaces the uXRCE-DDS + micro-ROS Agent path with a single
[zenoh-pico](https://github.com/eclipse-zenoh/zenoh-pico) node running directly
on the flight controller. The `zenoh` PX4 module bridges internal uORB topics to
the Zenoh wire protocol over Ethernet, using the same CDR serialisation and key
expression format as
[rmw_zenoh_cpp](https://github.com/ros2/rmw_zenoh), so ROS 2 Jazzy nodes
discover PX4 topics natively with no intermediate bridge process.

```
         PX4 (Nucleo-H753ZI)                       Host
┌──────────────────────────────────┐     ┌──────────────────────────────┐
│  uORB bus                        │     │  zenohd  (TCP :7447)         │
│   sensor_combined ──┐            │     │     │                        │
│   vehicle_attitude ─┤  zenoh     │ ETH │     │                        │
│   vehicle_status   ─┤  module ───┼─────┼─────┘                        │
│   ...              ─┤ (pub/sub)  │     │  ROS 2 (rmw_zenoh_cpp)       │
│   trajectory_sp ◄───┤            │     │   ros2 topic echo /fmu/out/… │
│   vehicle_command ◄─┘            │     └──────────────────────────────┘
└──────────────────────────────────┘
```

Key properties:

- No bridge process needed on the host when using `rmw_zenoh_cpp`.
- ROS 2 Jazzy+ compatible (RIHS01 type hash). Disable `CONFIG_ZENOH_KEY_TYPE_HASH`
  for Humble/Iron.
- Topics and QoS configured at runtime via NSH — no rebuild required.
- zenoh-pico is bundled at `src/modules/zenoh/zenoh-pico/`.

---

## 2. Implementation Architecture

### 2.1 Module Structure

The module is implemented as a standard PX4 module in `src/modules/zenoh/`:

```
class ZENOH : public ModuleBase<ZENOH>, public ModuleParams
```
(`src/modules/zenoh/zenoh.h:53`)

- Single PX4 task, 4096-byte stack, default scheduling priority.
- Owns `uORB_Zenoh_Publisher **_zenoh_publishers` and
  `Zenoh_Subscriber **_zenoh_subscribers` (zenoh.h:109, 111).
- Runtime parameters:

  | Parameter | Description | Default |
  |---|---|---|
  | `ZENOH_DOMAIN_ID` | ROS 2 / Zenoh domain ID | 0 |
  | `ZENOH_PUB_CC` | Congestion control (0=Drop, 1=Block) | 0 |
  | `ZENOH_PUB_REL` | Reliability (0=Reliable, 1=BestEffort) | 0 |
  | `ZENOH_PUB_EXPR` | Express mode (0=Off, 1=On) | 0 |
  | `ZENOH_PUB_PRIO` | Priority (1=RealTime … 7=Background) | 5 |

### 2.2 Session Lifecycle

**`ZENOH::setupSession()`** (`zenoh.cpp:216`):

1. Calls `z_config_default()` and inserts `mode` + `locator` read from
   `Zenoh_Config::getNetworkConfig()` (stored in `/fs/mtd_params/zenoh/net.cfg`).
2. Loops on `z_open()` until success, sleeping 5 s between retries:
   ```c
   do {
       // configure ...
       if (ret != 0) sleep(5);
   } while ((ret = z_open(&_s, z_move(config), NULL)) < 0);
   ```
3. Starts two background tasks:
   - `zp_start_read_task` — drives the TCP socket receive loop.
   - `zp_start_lease_task` — sends keep-alive renewals.
     Lease duration = 60 000 ms, matching the `rmw_zenoh_cpp` default.

**`ZENOH::cleanupSession()`** (`zenoh.cpp:440`):

1. Deletes all publisher and subscriber objects.
2. `zp_stop_read_task` / `zp_stop_lease_task`.
3. `z_drop(z_session_move(&_s))`.

### 2.3 Publisher Data Path (uORB → Zenoh)

**Class hierarchy:**

```
Zenoh_Publisher             (publishers/zenoh_publisher.hpp)
  └── uORB_Zenoh_Publisher  (publishers/uorb_publisher.hpp)
```

**Constructor** (`uorb_publisher.hpp`):
- Calls `orb_subscribe(meta)` or `orb_subscribe_multi(meta, instance)`.
- Stores `_cdr_ops` — a pointer to the CycloneDDS type ops table generated at
  build time for this message type.

**`uORB_Zenoh_Publisher::update()`** (called on `POLLIN`):

1. `orb_copy(_uorb_meta, _uorb_sub, data)` — reads latest uORB sample.
2. Prepends 4-byte ROS 2 CDR header `\x00\x01\x00\x00`.
3. `dds_stream_write(&os, &dds_allocator, data, _cdr_ops)` — encodes into CDR
   using the CycloneDDS stream encoder.
4. `Zenoh_Publisher::publish(buf, size)`:
   - Increments `_attachment.sequence_number`, records HRT timestamp.
   - `z_bytes_from_static_buf(&z_attachment, &_attachment, ...)` — attaches metadata.
   - `z_bytes_copy_from_buf(&payload, buf, size)` — wraps CDR payload.
   - `z_publisher_put(z_loan(_pub), z_move(payload), &options)`.

**Main loop** (`ZENOH::run()`, zenoh.cpp:476`):

```c
while (!should_exit()) {
    int pret = px4_poll(pfds, _pub_count, 100);  // 100 ms timeout
    for (i = 0; i < _pub_count; i++) {
        if (pfds[i].revents & POLLIN) {
            _zenoh_publishers[i]->update();
        }
    }
}
```

Each `pfds[i].fd` is the uORB subscription file descriptor set by
`uORB_Zenoh_Publisher::setPollFD()`.

> **Note:** Subscribers are purely event-driven (zenoh-pico read task calls
> `data_handler_cb`). They do not appear in the poll set.

### 2.4 Subscriber Data Path (Zenoh → uORB)

**Class hierarchy:**

```
Zenoh_Subscriber             (subscribers/zenoh_subscriber.hpp)
  └── uORB_Zenoh_Subscriber  (subscribers/uorb_subscriber.hpp)
```

**Constructor**: calls `orb_advertise()` or `orb_advertise_multi()` depending
on the `instance` field from `sub.cfg` (`-1` → new instance, `0` → default).

**`data_handler_cb`** (invoked by zenoh-pico read task on message arrival):

1. Validates payload length: must satisfy `4 ≤ len ≤ o_size + 4`.
2. **Fast path** (`Z_FEATURE_UNSTABLE_API`): `z_bytes_get_contiguous_view()` to
   decode directly from the zenoh buffer without a copy.
3. **Fallback path**: copies payload into a VLA, then decodes.
4. `dds_stream_read(&is, data, &dds_allocator, _cdr_ops)` — CDR deserialisation.
5. `fix_timestamp(data)` — overwrites the timestamp field with
   `hrt_absolute_time()` (no clock synchronisation with the host yet).
6. `orb_publish(_uorb_meta, _uorb_pub_handle, &data)` — writes to uORB.

### 2.5 ROS 2 Key Expression Format

All key expressions follow the `rmw_zenoh_cpp` convention so ROS 2 nodes
discover PX4 topics without a bridge.

**Data key expression** (`generate_rmw_zenoh_topic_keyexpr`):

```
<domain_id><zenoh_topic>/rt/<CamelCaseType>_/RIHS01_<32-byte-hex-hash>
```

Example:

```
0/fmu/out/vehicle_attitude/rt/VehicleAttitude_/RIHS01_aabb...ccdd
```

**Liveliness key expression** (`generate_rmw_zenoh_topic_liveliness_keyexpr`):

```
@ros2_lv/<domain_id>/<session-uuid>/0/11/<entity>/%%/%%/px4_<board-guid>
         /<topic>/rt/<Type>_/RIHS01_.../::,7:,:,:,,
```

`entity` = `"MP"` for publishers, `"MS"` for subscribers.

The RIHS01 hash implements ROS 2 REP-2016 Interface Definition Hashing, enabling
type-safe topic discovery in ROS 2 Jazzy and later.

> **Humble / Iron users:** add `# CONFIG_ZENOH_KEY_TYPE_HASH is not set` to
> `zenoh.px4board` before building to omit the hash from key expressions.

### 2.6 Configuration Backend

Three CSV files are stored under `/fs/mtd_params/zenoh/`:

| File | CSV format | Purpose |
|---|---|---|
| `net.cfg` | `mode;locator` | Connection mode and router locator |
| `pub.cfg` | `zenoh_topic;uorb_type;instance[;options]` | Publisher mappings |
| `sub.cfg` | `zenoh_topic;uorb_type;instance` | Subscriber mappings |

On first boot, `Zenoh_Config` constructor (`zenoh_config.cpp:61`) creates the
`/fs/mtd_params/zenoh/` directory and writes compiled-in defaults from
`default_pub_config` / `default_sub_config` (C string arrays generated from
`dds_topics.yaml` at build time).

Runtime edits via `zenoh config add/delete/net` write immediately to these
files. A `zenoh` task restart or board reboot is required to apply changes.

### 2.7 Code Generation Pipeline

```
src/modules/zenoh/dds_topics.yaml
        │  (topic list + per-topic QoS options)
        │
        ▼  generate_dds_topics.py  +  default_topics.c.em
        │  (CMakeLists.txt custom command)
        │
build/.../default_topics.c
        │  (default_pub_config / default_sub_config C strings)
        │
        ▼  Tools/zenoh/px_generate_zenoh_topic_files.py
        │
build/.../uorb_pubsub_factory.hpp
           (genPublisher / genSubscriber / getRIHS01_Hash per type)
```

`uorb_pubsub_factory.hpp` contains one typed instantiation per configured uORB
message. `ZENOH::setupTopics()` calls `genPublisher(type_name, instance)` and
`genSubscriber(type_name, instance)` with the string read from `pub.cfg` /
`sub.cfg` at runtime.

---

## 3. Build Configuration

### 3.1 `zenoh.px4board`

Place at `boards/st/nucleo-h753zi/zenoh.px4board`. Contains four overrides on
top of `default.px4board`:

| Key | Value | Reason |
|---|---|---|
| `CONFIG_BOARD_ETHERNET` | `y` | Links `px4_eth` network init into the build |
| `CONFIG_MODULES_ZENOH` | `y` | Includes the zenoh module |
| `CONFIG_MODULES_UXRCE_DDS_CLIENT` | `n` | Mutually exclusive with Zenoh |
| `CONFIG_ZENOH_PUB_OPTION_OVERRIDE` | `y` | Per-publisher QoS overrides; STM32H753 has sufficient flash |

### 3.2 `defconfig.fragment`

The current `nuttx-config/nsh/defconfig` contains no networking entries. The
fragment (in `zenoh_ref/nuttx-config/nsh/defconfig.fragment`) adds:

| Key | Purpose |
|---|---|
| `CONFIG_STM32H7_ETHMAC=y` | STM32H7 Ethernet MAC driver |
| `CONFIG_ETH0_PHY_LAN8742A=y` | On-board LAN8742A PHY (CN1 connector) |
| `CONFIG_NET_TCP=y` / `CONFIG_NET_UDP=y` | TCP and UDP socket support |
| `CONFIG_NET_TCP_WRITE_BUFFERS=y` / `CONFIG_NET_UDP_WRITE_BUFFERS=y` | Async TX (required by zenoh-pico) |
| `CONFIG_NETINIT_THREAD=y` | Bring up `eth0` automatically at boot |
| `CONFIG_NETINIT_IPADDR=0xC0A80004` | Static IP 192.168.0.4 (change as needed) |
| `CONFIG_NETINIT_DRIPADDR=0xC0A80001` | Default gateway 192.168.0.1 |
| `CONFIG_SYSTEM_DHCPC_RENEW=y` | DHCP renewal support |
| `CONFIG_NET_ICMP=y` / `CONFIG_NET_ICMP_SOCKET=y` | `ping` connectivity testing |

IP addresses are 32-bit big-endian hex: `0xAABBCCDD` = `AA.BB.CC.DD`.
To use DHCP, add `CONFIG_NETINIT_DHCPC=y` and remove the three
`CONFIG_NETINIT_*IPADDR` lines.

### 3.3 Notable Kconfig Options

(`src/modules/zenoh/Kconfig`)

| Option | Default | Notes |
|---|---|---|
| `ZENOH_DEFAULT_LOCATOR` | `tcp/10.41.10.1:7447#iface=eth0` | Override at runtime with `zenoh config net` |
| `ZENOH_RMW_LIVELINESS` | `y` | Liveliness tokens for ROS 2 graph discovery |
| `ZENOH_KEY_TYPE_HASH` | `y` | RIHS01 hash in key expressions (Jazzy+) |
| `ZENOH_PUB_OPTION_OVERRIDE` | `n` (set `y` in `zenoh.px4board`) | Per-publisher QoS |
| `ZENOH_PUBSUB_SELECTION` | `ALL` | Switch to `MINIMAL` to reduce flash usage |

---

## 4. Integration Workflow

### Prerequisites

- ARM GCC toolchain (`arm-none-eabi-gcc` ≥ 10)
- ST-Link v2/v3 or DAPLink connected to Nucleo-H753ZI SWD header (CN4)
- RJ-45 Ethernet cable from board CN1 to a switch or directly to the host
- Python 3 with empy and jinja2: `pip install empy jinja2`

### Step 1 — Merge the NuttX defconfig fragment

```sh
cat boards/st/nucleo-h753zi/zenoh_ref/nuttx-config/nsh/defconfig.fragment \
    >> boards/st/nucleo-h753zi/nuttx-config/nsh/defconfig
```

Optionally review and normalise:

```sh
make st_nucleo-h753zi_zenoh menuconfig
make st_nucleo-h753zi_zenoh savedefconfig
```

To customise the static IP, locate `CONFIG_NETINIT_IPADDR` in the defconfig and
replace the hex value (network byte order: `0xC0A80004` = `192.168.0.4`).

### Step 2 — Place the board variant file

```sh
cp boards/st/nucleo-h753zi/zenoh_ref/zenoh.px4board \
   boards/st/nucleo-h753zi/zenoh.px4board
```

### Step 3 — Build

```sh
make st_nucleo-h753zi_zenoh
```

Expected artefact: `build/st_nucleo-h753zi_zenoh/px4_nucleo-h753zi_zenoh.px4`

### Step 4 — Flash

```sh
make st_nucleo-h753zi_zenoh upload
# or via OpenOCD:
make st_nucleo-h753zi_zenoh upload UPLOADER=openocd
```

### Step 5 — Connect to NSH

```sh
# Find the CDC-ACM device
ls /dev/ttyACM*

# Connect (57600 baud)
minicom -D /dev/ttyACM0 -b 57600
# or
screen /dev/ttyACM0 57600
```

### Step 6 — Verify Ethernet link

```text
nsh> ifconfig
eth0    Link encap:Ethernet  HWaddr xx:xx:xx:xx:xx:xx
        inet addr:192.168.0.4  Bcast:192.168.0.255  Mask:255.255.255.0

nsh> ping 192.168.0.1
```

> If `eth0` is absent, the `defconfig.fragment` was not merged correctly.
> Re-check `nuttx-config/nsh/defconfig` and rebuild.

### Step 7 — Start zenohd on the host

```sh
# Option A: standalone Zenoh router
cargo install zenohd
zenohd

# Option B: bundled with rmw_zenoh_cpp (ROS 2 Jazzy)
ros2 run rmw_zenoh_cpp rmw_zenohd &
```

### Step 8 — Configure the Zenoh locator

From NSH (replace `192.168.0.1` with your host IP):

```text
nsh> zenoh config net client tcp/192.168.0.1:7447#iface=eth0
```

For multicast peer discovery (no fixed router):

```text
nsh> zenoh config net peer udp/224.0.0.224:7446#iface=eth0
```

The locator is written to `/fs/mtd_params/zenoh/net.cfg` immediately.

### Step 9 — Apply parameters and enable

```text
nsh> sh /etc/init.d/rc.board_zenoh
nsh> param save
nsh> reboot
```

Or set individually:

```text
nsh> param set ZENOH_ENABLE 1
nsh> param set ZENOH_DOMAIN_ID 0
nsh> param save
nsh> reboot
```

### Step 10 — Add topic mappings

On first boot the default mappings from `dds_topics.yaml` are written to flash.
To add custom mappings after reboot:

```text
nsh> zenoh config add publisher /fmu/out/sensor_combined sensor_combined
nsh> zenoh config add publisher /fmu/out/vehicle_attitude vehicle_attitude 0 cc=drop,express=true,rel=best_effort
nsh> zenoh config add subscriber /fmu/in/trajectory_setpoint trajectory_setpoint
```

Changes to `pub.cfg` / `sub.cfg` take effect on next `zenoh start` or reboot.

### Step 11 — Verify on board

```text
nsh> zenoh status
Connected
Publishers
  uORB sensor_combined -> 0/fmu/out/sensor_combined/rt/SensorCombined_/RIHS01_...
  uORB vehicle_attitude -> 0/fmu/out/vehicle_attitude/rt/VehicleAttitude_/RIHS01_...
Subscribers
  Topic: 0/fmu/in/trajectory_setpoint/rt/TrajectorySetpoint_/... -> uORB trajectory_setpoint
```

### Step 12 — Verify from host (ROS 2)

```sh
export RMW_IMPLEMENTATION=rmw_zenoh_cpp
export RMW_ZENOH_DOMAIN_ID=0   # must match ZENOH_DOMAIN_ID param

ros2 topic list
# /fmu/out/sensor_combined
# /fmu/out/vehicle_attitude
# ...

ros2 topic echo /fmu/out/sensor_combined px4_msgs/msg/SensorCombined
```

---

## 5. QoS Configuration

Zenoh QoS is configured at two levels.

### 5.1 Global Parameters

Applied to all publishers that have no per-publisher override:

| Parameter | NSH command | Effect |
|---|---|---|
| `ZENOH_PUB_CC` | `param set ZENOH_PUB_CC 0` | 0=Drop, 1=Block |
| `ZENOH_PUB_REL` | `param set ZENOH_PUB_REL 0` | 0=Reliable, 1=BestEffort |
| `ZENOH_PUB_EXPR` | `param set ZENOH_PUB_EXPR 1` | 0=Off, 1=Express (bypass batching) |
| `ZENOH_PUB_PRIO` | `param set ZENOH_PUB_PRIO 5` | 1=RealTime … 7=Background |

All require a reboot to take effect.

### 5.2 Per-Publisher Overrides

Available when `CONFIG_ZENOH_PUB_OPTION_OVERRIDE=y` (set in `zenoh.px4board`).

```text
zenoh config add publisher <zenoh_topic> <uorb_type> [instance] [key=val,...]
```

| Key | Values | Description |
|---|---|---|
| `cc` | `drop`, `block` | Congestion control |
| `express` | `true`, `false` | Bypass internal batching for lower latency |
| `prio` | `real_time`, `interactive_high`, `interactive_low`, `data_high`, `data`, `data_low`, `background` | Message priority |
| `rel` | `reliable`, `best_effort` | Delivery reliability |

### 5.3 Recommended Profiles

| Topic category | Recommended options |
|---|---|
| High-rate telemetry (attitude, local position, odometry) | `cc=drop,express=true,rel=best_effort` |
| Command / arming messages | `cc=block,rel=reliable,express=true` |
| Low-rate status (battery, land detected) | global defaults |

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `zenoh status` shows "Connecting" indefinitely | No route to zenohd, wrong IP, or zenohd not running | `ping <host-ip>` from NSH; verify zenohd listens on port 7447; check `net.cfg` with `zenoh config` |
| `ifconfig` shows no `eth0` | `defconfig.fragment` not merged | Re-append fragment to `nuttx-config/nsh/defconfig` and rebuild |
| Build error: `MODULES_ZENOH` undefined | `zenoh.px4board` not placed | Copy `zenoh_ref/zenoh.px4board` to the board directory |
| ROS 2 sees no topics | Wrong RMW or domain ID mismatch | `export RMW_IMPLEMENTATION=rmw_zenoh_cpp`; verify `RMW_ZENOH_DOMAIN_ID` matches `ZENOH_DOMAIN_ID` param |
| Topics invisible in ROS 2 Humble/Iron | RIHS01 hash not understood | Add `# CONFIG_ZENOH_KEY_TYPE_HASH is not set` to `zenoh.px4board` and rebuild |
| `zenoh config add` prints "not found" | uORB type name typo | Check exact type names in `src/modules/zenoh/dds_topics.yaml` |
| High latency on attitude / position topics | Express mode disabled or reliable delivery | Use `cc=drop,express=true,rel=best_effort` |
| Firmware too large to flash | Too many Zenoh topic stubs compiled in | Set `CONFIG_ZENOH_PUBSUB_SELECTION=MINIMAL` in `zenoh.px4board` |
