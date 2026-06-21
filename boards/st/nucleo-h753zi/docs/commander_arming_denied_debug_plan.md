# Commander Arming Denied Debug Plan

This runbook is for cases where PX4 refuses to arm with a message such as
`Arming denied: Resolve system health failures first`, `Preflight check:
FAILED`, or QGroundControl shows a preflight/arming failure. It is written for
the ST Nucleo-H753ZI HITL target, but most commands apply to any PX4 build with
the `commander`, `listener`, `param`, and `mavlink` commands enabled.

Related source:

| Area | Source |
|---|---|
| Direct arm gate | `src/modules/commander/Commander.cpp`, `Commander::arm()` |
| Check framework | `src/modules/commander/HealthAndArmingChecks/*` |
| Mode requirements | `src/modules/commander/ModeUtil/mode_requirements.cpp` |
| uORB result topics | `msg/HealthReport.msg`, `msg/FailsafeFlags.msg`, `msg/versioned/VehicleStatus.msg`, `msg/ActuatorArmed.msg` |

## Expected Debug Outcome

At the end of the debug pass, identify one of these:

| Result | Meaning |
|---|---|
| Direct arm gate failed | Commander denied before health checks could decide, for example calibration active, unsafe throttle, kill/termination active, or safety still on. |
| Current mode cannot arm | The vehicle may be healthy, but the selected mode requires missing inputs such as manual control, position, mission, home, or offboard setpoints. |
| Health component failed | Required sensor, estimator, power, battery, ESC, storage, or subsystem health is bad or stale. |
| HITL data path failed | On Nucleo-H753ZI, simulated sensor/GPS/baro/mag data is missing, stale, or EKF2 has not accepted it yet. |
| Parameter mismatch | Saved parameters override board defaults and re-enable checks that are not valid for this HITL board. |

Do not start by force arming. First collect the denial reason, because force
arming skips useful evidence and can hide the actual failure.

## 1. Capture the Symptom

Run the explicit pre-arm check and keep the console output:

```sh
commander check
```

Then capture the current commander state:

```sh
commander status
listener vehicle_status 1
listener actuator_armed 1
listener health_report 1
listener failsafe_flags 1
```

Interpret the first pass:

| Field or output | Good value | If bad |
|---|---|---|
| `commander check` | `Preflight check: OK` | Continue with this plan. |
| `vehicle_status.pre_flight_checks_pass` | `true` before normal arm | If false, health/mode checks currently block arming. |
| `actuator_armed.ready_to_arm` | `true` when disarmed and ready | If false, current mode's `can_arm` bit is not set. |
| `vehicle_status.arming_state` | `ARMING_STATE_DISARMED` before arming | If already armed, the problem is not pre-arm denial. |
| `health_report.can_arm_mode_flags` | Bit for current `nav_state` is set | If not set, decode `failsafe_flags` and health flags. |
| `failsafe_flags` | Failure booleans false unless expected | True flags are the most useful next clue. |

For `health_report.can_arm_mode_flags`, the current mode bit is
`1 << vehicle_status.nav_state`. For example, `AUTO_LOITER` is nav state `4`,
so bit `16` must be present in `can_arm_mode_flags`.

## 2. Check Direct Commander Gates

These conditions deny arming before or around the normal health-check result.

| Check | How to inspect | What to do |
|---|---|---|
| Calibration active | `listener vehicle_status 1`, check `calibration_enabled` and `rc_calibration_in_progress`; `listener actuator_armed 1`, check `in_esc_calibration_mode` | Wait for calibration to finish, cancel it, or reboot if it is stuck. |
| Kill or termination active | `listener actuator_armed 1`, check `kill` and `termination`; `listener vehicle_status 1`, check `nav_state == TERMINATION` | Clear kill if intentional, exit termination only through the appropriate recovery path, then reboot if needed. |
| Safety still on | `listener vehicle_status 1`, check `safety_button_available` and `safety_off` | Press the safety button, or use `commander safety off` on a bench/HITL setup where that is appropriate. |
| Unsafe manual throttle | Check the arm-denied log text after `commander arm`; inspect manual input with `listener manual_control_setpoint 1` | Put throttle in the safe position, or select an autonomous mode for Nucleo HITL. |
| USB safety check | `listener vehicle_status 1`, check `usb_connected`; check `param show CBRK_USB_CHK` | Disconnect unsafe USB if the board requires it, or use the intended development circuit breaker only for bench testing. |
| VTOL transition or fixed-wing arming state | `listener vehicle_status 1`, check `is_vtol`, `in_transition_mode`, and `vehicle_type` | Wait for transition to finish or switch to multicopter mode before arming. |
| Arm authorization | Check `param show COM_ARM_AUTH_REQ` and QGC/MAVLink messages | If enabled, verify the authorizer replies and accepts the request. |

On Nucleo-H753ZI HITL, the common direct-gate issue is wrong mode plus missing
manual throttle/input. Use `auto:loiter` for normal HITL arming:

```sh
commander mode auto:loiter
commander check
commander arm
```

## 3. Check the Current Mode First

Commander evaluates readiness against the current `vehicle_status.nav_state`.
A vehicle can be healthy enough to arm in one mode and denied in another.

```sh
commander status
listener vehicle_status 1
listener health_report 1
```

Key mode facts:

| Mode | Common arming requirement |
|---|---|
| Manual | Manual control signal required. |
| Stabilized / Altitude / Position | Manual control plus attitude/angular velocity; altitude/position modes need estimator state. |
| Auto Loiter | Position, attitude, angular velocity, and altitude estimates. No manual input requirement. |
| Auto Mission | Same core navigation estimates plus a valid mission. |
| Offboard | Recent offboard signal and setpoints; may also require position, velocity, or attitude depending on offboard mode bits. |
| RTL / Land / Descend / Termination / Follow / Orbit / Precision Land | Many are marked as not suitable for arming. Switch to a suitable mode first. |

For Nucleo HITL with `COM_RC_IN_MODE=4`, manual input is ignored. Do not debug
Manual/Stabilized/Altitude/Position first; switch to Hold/`auto:loiter`.

## 4. Decode `failsafe_flags`

`failsafe_flags` shows the state that `ModeChecks` uses to clear `can_arm` and
`can_run` bits. Start with every true flag and inspect the matching topic.

| True flag or suspicious field | Likely cause | Check with | Typical fix |
|---|---|---|---|
| `angular_velocity_invalid` | No fresh gyro/vehicle angular velocity data | `listener vehicle_angular_velocity 1`, `listener sensor_gyro 1` | Fix sensor/HITL stream; restart simulator or sensors. |
| `attitude_invalid` | EKF attitude not valid or stale | `listener vehicle_attitude 1`, `listener estimator_status_flags 1` | Wait for EKF alignment; check gyro/accel/mag/GPS inputs. |
| `local_altitude_invalid` | No valid local altitude estimate | `listener vehicle_local_position 1`, `listener vehicle_air_data 1`, `listener estimator_status_flags 1` | Restore baro/GPS HIL data and EKF height alignment. |
| `local_position_invalid` or `_relaxed` | EKF local XY invalid or too inaccurate | `listener vehicle_local_position 1`, `listener estimator_status 1`, `listener estimator_status_flags 1` | Wait for GPS/local aiding; check GPS quality and heading. |
| `global_position_invalid` or `_relaxed` | Global position invalid/stale | `listener vehicle_global_position 1`, `listener vehicle_gps_position 1` | Restore HIL GPS or GPS driver data; wait for fix/fusion. |
| `local_velocity_invalid` | Local velocity invalid, often affects offboard velocity | `listener vehicle_local_position 1` | Fix estimator aiding or select a mode not requiring velocity. |
| `auto_mission_missing` | No valid uploaded mission | `listener mission_result 1` | Upload a mission or switch out of Mission mode. |
| `offboard_control_signal_lost` | No recent offboard signal | `listener offboard_control_mode 1` | Start the offboard publisher before switching/arming in Offboard. |
| `home_position_invalid` | Home not set | `listener home_position 1` | Wait for position/home setup; avoid modes requiring home until valid. |
| `manual_control_signal_lost` | No RC/joystick/manual setpoint | `listener manual_control_setpoint 1`, `param show COM_RC_IN_MODE` | Connect manual input or use an autonomous mode. |
| `gcs_connection_lost` | GCS telemetry link not present | `mavlink status`, `listener telemetry_status 1`, `param show NAV_DLL_ACT` | Restore telemetry or keep `NAV_DLL_ACT=0` for Nucleo HITL. |
| `battery_unhealthy` or `battery_warning` | Battery missing, low, failed, stale | `listener battery_status 1`, `param show CBRK_SUPPLY_CHK` | Fix battery source or use HITL supply breaker only on bench. |
| `fd_critical_failure`, `fd_alt_loss`, `fd_motor_failure`, `fd_esc_arming_failure` | Failure detector or ESC/motor failure | `listener failure_detector_status 1`, `listener esc_status 1`, `listener actuator_armed 1` | Resolve failure, clear kill/termination, reboot if latched. |
| `geofence_breached` | Geofence active and currently violated | `listener geofence_result 1`, `param show GF_ACTION` | Move inside fence, change fence/action, or disable only for controlled testing. |
| `mission_failure` or `navigator_failure` | Navigator cannot execute selected mode | `listener navigator_status 1`, `listener mission_result 1` | Fix mission, rally/geofence/home constraints, or select another mode. |
| `parachute_unhealthy`, `remote_id_unhealthy` | Required subsystem missing/unhealthy | `listener vehicle_status 1`, `param show COM_PARACHUTE COM_ARM_ODID` | Connect subsystem or change requirement only if the vehicle configuration permits. |
| `gnss_lost` | Required GNSS count/fix lost or dual-GNSS divergence | `listener sensor_gps 1`, `param show SYS_HAS_NUM_GNSS COM_GNSSLOSS_ACT` | Restore GPS data/fix or correct GNSS requirement parameters. |

## 5. Decode `health_report`

`health_report` is the compact health and arming result. It does not name each
event, but it tells whether the current mode can arm and which component groups
have warning/error flags.

```sh
listener health_report 1
```

Use these fields:

| Field | Meaning |
|---|---|
| `can_arm_mode_flags` | Bitfield of navigation states that can arm now. Current `nav_state` bit must be set. |
| `can_run_mode_flags` | Bitfield of navigation states that can be entered/run while armed. Useful when mode changes are denied. |
| `health_is_present_flags` | Components currently present. |
| `health_warning_flags`, `health_error_flags` | Hardware/system health issues. |
| `arming_check_warning_flags`, `arming_check_error_flags` | Pre-arm failures that are not necessarily hardware health failures. |

If the health report says the current mode cannot arm, but you do not know why,
run `commander check` again and read the event/MAVLink messages in the shell or
QGroundControl. The detailed text is emitted by the individual check that failed.

## 6. Nucleo-H753ZI HITL Data Path Checks

This board has no onboard flight sensors in the default HITL configuration.
Arming depends on simulator data arriving over MAVLink and being accepted by
EKF2.

First verify the board defaults have not been overridden by saved parameters:

```sh
param show SYS_HITL
param show SYS_HAS_MAG
param show SYS_HAS_BARO
param show SYS_HAS_GPS
param show COM_ARM_WO_GPS
param show COM_ARM_MAG_STR
param show CBRK_SUPPLY_CHK
param show CBRK_IO_SAFETY
param show COM_RC_IN_MODE
param show NAV_DLL_ACT
param show COM_ARM_ODID
param show BAT1_SOURCE
```

Expected values for normal Nucleo HITL:

| Parameter | Expected |
|---|---:|
| `SYS_HITL` | `1` |
| `SYS_HAS_MAG` | `1` |
| `SYS_HAS_BARO` | `1` |
| `SYS_HAS_GPS` | `1` |
| `COM_ARM_WO_GPS` | `1` |
| `COM_ARM_MAG_STR` | `0` |
| `CBRK_SUPPLY_CHK` | `894281` |
| `CBRK_IO_SAFETY` | `220127` |
| `COM_RC_IN_MODE` | `4` |
| `NAV_DLL_ACT` | `0` |
| `COM_ARM_ODID` | `0` |
| `BAT1_SOURCE` | `0` |

Then verify the HITL stream:

```sh
mavlink status
pwm_out_sim status
listener sensor_accel 1
listener sensor_gyro 1
listener sensor_mag 1
listener vehicle_air_data 1
listener vehicle_gps_position 1
listener vehicle_attitude 1
listener vehicle_local_position 1
listener vehicle_global_position 1
listener estimator_status_flags 1
```

Expected before arming in `auto:loiter`:

| Topic | Expected sign |
|---|---|
| `sensor_accel`, `sensor_gyro`, `sensor_mag` | Fresh timestamps and nonzero simulation device IDs. |
| `vehicle_air_data` | Fresh barometer-derived air data. |
| `vehicle_gps_position` | Fresh GPS with `fix_type >= 3`. |
| `vehicle_attitude` | Fresh quaternion. |
| `vehicle_local_position` | `xy_valid`, `z_valid`, and reasonable `eph`/`evh`. |
| `vehicle_global_position` | `lat_lon_valid` and `alt_valid`. |
| `estimator_status_flags` | Yaw aligned, height aligned, and GNSS/local position aiding active enough for selected mode. |

If these topics are stale or missing, fix the MAVLink/HITL connection before
debugging commander further.

## 7. Common Fix Recipes

| Symptom | Fastest useful action |
|---|---|
| `Preflight Fail: No manual control input` on Nucleo HITL | Run `commander mode auto:loiter`, then `commander check`. Do not arm in manual-control modes with `COM_RC_IN_MODE=4`. |
| `No valid attitude estimate` | Check `sensor_accel`, `sensor_gyro`, `vehicle_attitude`, and `estimator_status_flags`; wait for EKF2 to initialize after simulator start. |
| `No valid position estimate` | Check GPS, local/global position, and EKF flags. Verify jMAVSim/Gazebo is sending HIL GPS and the vehicle has a fix. |
| `Global position estimate required` or `Home position required` | Check `COM_ARM_WO_GPS`; for strict GPS arming, wait for global and home position. |
| `Power module not connected` or battery failure on Nucleo HITL | Check `CBRK_SUPPLY_CHK=894281` and `BAT1_SOURCE=0`; reset saved params if old values override defaults. |
| `USB connected` | This is normally relaxed on development boards by `CBRK_USB_CHK`; if enabled, disconnect unsafe USB or restore intended bench config. |
| `Press safety button first` | Press safety or run `commander safety off` only in a controlled bench/HITL setup. |
| `Mode not suitable for arming` | Switch to a suitable mode such as `auto:loiter`; avoid RTL/Land/Descend/Termination as arming modes. |
| `No valid mission available` | Upload a mission or leave Mission mode. |
| `No offboard signal` | Start the offboard setpoint stream before selecting/arming Offboard. |

## 8. Reset Known Nucleo HITL Defaults

If saved flash parameters are suspected, reset the HITL-related defaults:

```sh
param reset SYS_AUTOSTART SYS_HITL SYS_HAS_MAG SYS_HAS_BARO SYS_HAS_GPS
param reset EKF2_GPS_CTRL EKF2_HGT_REF EKF2_BARO_CTRL EKF2_MAG_TYPE EKF2_MAG_CHECK EKF2_EV_CTRL
param reset SENS_IMU_MODE EKF2_MULTI_IMU
param reset EKF2_REQ_EPH EKF2_REQ_EPV EKF2_REQ_HDRIFT EKF2_REQ_VDRIFT EKF2_DELAY_MAX
param reset COM_ARM_WO_GPS COM_ARM_MAG_STR CBRK_SUPPLY_CHK CBRK_IO_SAFETY COM_RC_IN_MODE COM_DISARM_PRFLT
param reset GPS_1_CONFIG GPS_2_CONFIG RC_PORT_CONFIG MAV_0_CONFIG MAV_1_CONFIG MAV_2_CONFIG
param reset SYS_USB_AUTO USB_MAV_MODE NAV_DLL_ACT COM_ARM_ODID BAT1_SOURCE
param save
reboot
```

After reboot, start the simulator, wait for estimator alignment, then retry:

```sh
commander mode auto:loiter
commander check
commander arm
```

## 9. Evidence to Save When Escalating

When the cause is not obvious, save this block in the issue or lab notes:

```sh
commander status
commander check
listener vehicle_status 1
listener actuator_armed 1
listener health_report 1
listener failsafe_flags 1
listener estimator_status_flags 1
listener vehicle_local_position 1
listener vehicle_global_position 1
listener vehicle_gps_position 1
listener sensor_accel 1
listener sensor_gyro 1
listener sensor_mag 1
listener vehicle_air_data 1
mavlink status
param show SYS_HITL
param show COM_RC_IN_MODE
param show COM_ARM_WO_GPS
param show CBRK_SUPPLY_CHK
param show NAV_DLL_ACT
```

Include the selected mode, simulator used, USB device path, and whether the
denial came from QGroundControl, `commander arm`, or an RC/action request.

## 10. Force Arming Policy

`commander arm -f` sends the MAVLink force magic value. Use it only for
controlled bench experiments when actuator output cannot create a hazard and
the reason for denial is already understood. Do not use force arming to bypass
unknown estimator, sensor, power, battery, kill, termination, or mode failures.
