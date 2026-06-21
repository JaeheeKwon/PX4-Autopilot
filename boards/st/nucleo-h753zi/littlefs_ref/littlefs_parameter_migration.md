# Nucleo-H753ZI LittleFS Parameter Storage Migration

This document describes how to migrate `boards/st/nucleo-h753zi` from the
current raw flashfs parameter backend to file-backed PX4 parameters stored on a
LittleFS volume.

The reference files live in:

```text
boards/st/nucleo-h753zi/littlefs_ref/
```

They are reference material only. The active board still uses raw flashfs until
the files listed below are merged into `boards/st/nucleo-h753zi`.

## Goal

After migration, the parameter path must resolve like this:

```text
board_app_initialize()
  -> creates an MTD partition from internal flash
  -> mounts LittleFS at /fs/flash
  -> rcS sources generated rc.filepaths
  -> rcS runs: param select /fs/flash/params
  -> param load-or-init loads or creates /fs/flash/params
  -> later param save writes the BSON parameter file to LittleFS
```

The important point is that the `param` module does not discover LittleFS by
itself. It only uses LittleFS when:

1. the flash backend is not compiled through `FLASH_BASED_PARAMS`, and
2. `param select` receives a normal mounted file path.

## Current Active State

The active board currently uses flashfs directly:

| Area | Current value |
|---|---|
| Parameter backend selector | `FLASH_BASED_PARAMS` in `src/board_config.h` |
| Board init storage setup | `parameter_flashfs_init()` in `src/init.c` |
| Flash reservation | one 128 KiB sector |
| Generated parameter path | `/fs/mtd_params` |
| App flash window | `0x08020000` plus 1792 KiB |

While `FLASH_BASED_PARAMS` is defined, `param select <file>` does not select a
file-backed default store. The `param` library ignores the selected file for
default persistence and keeps using the flash backend.

## Target State

The intended LittleFS state is:

| Area | Target value |
|---|---|
| Parameter backend selector | no `FLASH_BASED_PARAMS` define |
| Board init storage setup | `progmem_initialize()` -> `mtd_partition()` -> `register_mtddriver()` -> `nx_mount(..., "littlefs", ..., "autoformat")` |
| LittleFS mountpoint | `/fs/flash` |
| Parameter file | `/fs/flash/params` |
| LittleFS flash reservation | sectors 12-15, 512 KiB total |
| App flash window | sectors 1-11, 1408 KiB total |

## Migration Steps

### 1. Use parameter-only storage

- Keep `CONFIG_BOARD_ROOT_PATH` separate from the LittleFS volume.
- Set only `CONFIG_BOARD_PARAM_FILE="/fs/flash/params"`.
- Mount LittleFS explicitly at `/fs/flash` in `src/init.c`.

This keeps the tiny LittleFS partition dedicated to parameters and avoids
having `rcS` search it for config scripts, backups, hardfault logs, external
airframes, and update directories.

### 2. Reserve flash for LittleFS

Update `boards/st/nucleo-h753zi/nuttx-config/scripts/script.ld`.

Change the active flash window from:

```ld
FLASH      (rx) : ORIGIN = 0x08020000, LENGTH = 1792K /* params in last sector */
```

to:

```ld
FLASH      (rx) : ORIGIN = 0x08020000, LENGTH = 1408K /* LittleFS params in sectors 12-15 */
```

This keeps the app in sectors 1-11 and leaves sectors 12-15 for LittleFS.

### 3. Update bootloader flash limits

Update `boards/st/nucleo-h753zi/src/hw_config.h`.

Change:

```c
#define BOARD_FLASH_SECTORS            (14)
#define APP_RESERVATION_SIZE           (1 * 128 * 1024)
```

to:

```c
#define BOARD_FLASH_SECTORS            (11)
#define APP_RESERVATION_SIZE           (4 * 128 * 1024)
```

This makes the bootloader agree with the linker script. Without this, a firmware
upload can erase or write sectors that LittleFS owns.

### 4. Update firmware image metadata

Update `boards/st/nucleo-h753zi/firmware.prototype`.

Change:

```json
"image_maxsize": 1835008
```

to:

```json
"image_maxsize": 1441792
```

This is 1408 KiB. It must match the app flash window from the linker script.

### 5. Remove the flashfs parameter backend

Update `boards/st/nucleo-h753zi/src/board_config.h`.

Remove:

```c
/* Store params in internal flash */
#define FLASH_BASED_PARAMS
```

Do not leave the define commented near active code in a way that could be
re-enabled accidentally. With this define gone, `param select` can select the
file-backed default parameter store.

### 6. Mount LittleFS during board initialization

Update `boards/st/nucleo-h753zi/src/init.c`.

Remove the flashfs include and initialization block:

```c
#if defined(FLASH_BASED_PARAMS)
#include <parameters/flashparams/flashfs.h>
#endif
```

and:

```c
#if defined(FLASH_BASED_PARAMS)
static sector_descriptor_t params_sector_map[] = {
	{15, 128 * 1024, 0x081E0000},
	{0, 0, 0},
};
int result = parameter_flashfs_init(params_sector_map, NULL, 0);
...
#endif
```

Replace it with a LittleFS mount helper based on
`boards/st/nucleo-h753zi/littlefs_ref/src/init.c`.

Keep the mountpoint independent from `CONFIG_BOARD_ROOT_PATH`:

```c
#define PARAM_LITTLEFS_DEVICE       "/dev/mtd_params"
#define PARAM_LITTLEFS_MOUNTPOINT   "/fs/flash"
#define PARAM_LITTLEFS_ERASE_BLOCKS 4
#define PARAM_LITTLEFS_TEST_FILE    PARAM_LITTLEFS_MOUNTPOINT "/.mount_test"
```

The helper must:

1. call `progmem_initialize()`;
2. query `MTDIOC_GEOMETRY`;
3. partition the final four erase blocks;
4. register the partition as `/dev/mtd_params`;
5. create `/fs` and `/fs/flash`;
6. mount `/dev/mtd_params` as LittleFS at `/fs/flash` with `autoformat`;
7. create and remove a small test file to confirm the filesystem is writable.

Call the helper from `board_app_initialize()` before `px4_platform_configure()`
returns and before `rcS` starts.

### 7. Point generated rc.filepaths at the LittleFS parameter file

Update `boards/st/nucleo-h753zi/default.px4board`.

Add:

```sh
CONFIG_BOARD_PARAM_FILE="/fs/flash/params"
```

Do not add `CONFIG_BOARD_ROOT_PATH="/fs/flash"`. Let the board root path remain
the existing default unless a separate requirement needs it.

After rebuild, confirm:

```sh
cat build/st_nucleo-h753zi_default/etc/init.d/rc.filepaths
```

Expected:

```sh
set PARAM_FILE /fs/flash/params
set BOARD_ROOT_PATH /fs/microsd
```

### 8. Add rc.board_early as a storage guard

Add:

```text
boards/st/nucleo-h753zi/init/rc.board_early
```

using:

```text
boards/st/nucleo-h753zi/littlefs_ref/init/rc.board_early
```

This disables generic storage handling so the parameter partition is not used
for backups, hardfault logs, external airframes, or update directories.

### 9. Merge LittleFS NuttX tuning

Update `boards/st/nucleo-h753zi/nuttx-config/nsh/defconfig`.

The active defconfig already enables:

```text
CONFIG_FS_LITTLEFS=y
```

Merge the tuning from
`boards/st/nucleo-h753zi/littlefs_ref/nuttx-config/nsh/defconfig.fragment`:

```text
CONFIG_FS_LITTLEFS_PROGRAM_SIZE_FACTOR=1
CONFIG_FS_LITTLEFS_READ_SIZE_FACTOR=1
CONFIG_FS_LITTLEFS_CACHE_SIZE_FACTOR=1
CONFIG_FS_LITTLEFS_BLOCK_CYCLE=-1
```

These settings keep the small internal LittleFS volume parameter-focused and
avoid metadata relocation behavior that expects more spare erase blocks.

### 10. Rebuild

Clean enough build output to regenerate Kconfig and ROMFS outputs, then build:

```sh
make st_nucleo-h753zi_default
```

If the image exceeds 1408 KiB, trim unused modules before changing the LittleFS
layout. The current HITL-focused image was close to this limit, so keep an eye
on image size.

Useful checks:

```sh
cat build/st_nucleo-h753zi_default/etc/init.d/rc.filepaths
ls -l build/st_nucleo-h753zi_default/st_nucleo-h753zi_default.bin
```

### 11. Flash and first boot behavior

The first boot after migration formats sectors 12-15 as LittleFS. Existing
flashfs parameters in sector 15 are erased.

Boot logs should show the LittleFS mount message from `src/init.c`. From NSH:

```sh
dmesg
ls /fs
ls /fs/flash
param status
```

Expected filesystem state after first parameter initialization:

```text
/fs/flash/params
```

### 12. Validate parameter persistence

From NSH or the MAVLink console:

```sh
param set COM_DISARM_PRFLT -1
param save
ls /fs/flash
reboot
param show COM_DISARM_PRFLT
param status
```

Expected:

- `/fs/flash/params` exists.
- `COM_DISARM_PRFLT` keeps the saved value across reboot.
- `param status` reports the selected default file path.
- `parameters_backup.bson` is absent unless parameter backups were deliberately
  enabled.

## Failure Modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `param status` still shows flash backend behavior | `FLASH_BASED_PARAMS` is still defined | Remove the define from `src/board_config.h` and rebuild |
| `param save` fails to open `/fs/flash/params` | LittleFS was not mounted before `rcS` reached `param select` | Check `board_app_initialize()` mount path and `dmesg` |
| Generated `rc.filepaths` still contains `/fs/mtd_params` | `CONFIG_BOARD_PARAM_FILE` was not changed or build output is stale | Update `default.px4board`, regenerate, and rebuild |
| Firmware upload succeeds but parameters later corrupt | bootloader/linker/image metadata disagree about reserved sectors | Recheck `script.ld`, `hw_config.h`, and `firmware.prototype` |
| `/fs/flash` contains logs, backup files, or config directories | `/fs/flash` was made `BOARD_ROOT_PATH` without disabling storage features | Add `rc.board_early` or keep `BOARD_ROOT_PATH` separate |
| Build exceeds flash limit | app image no longer fits sectors 1-11 | Remove unused modules or reduce LittleFS reservation only after reassessing update safety |

## Final Checklist

- `FLASH_BASED_PARAMS` removed from active `src/board_config.h`.
- `parameter_flashfs_init()` removed from active `src/init.c`.
- LittleFS MTD partition and mount helper added to active `src/init.c`.
- LittleFS mountpoint is `/fs/flash`.
- `CONFIG_BOARD_PARAM_FILE="/fs/flash/params"` is set.
- Generated `rc.filepaths` selects `/fs/flash/params`.
- Linker app flash length is 1408 KiB.
- Bootloader app flash sectors end at sector 11.
- Firmware `image_maxsize` is 1441792.
- NuttX LittleFS tuning options are merged.
- First boot formats LittleFS successfully.
- `param save` creates `/fs/flash/params`.
- Saved parameter values survive reboot.
