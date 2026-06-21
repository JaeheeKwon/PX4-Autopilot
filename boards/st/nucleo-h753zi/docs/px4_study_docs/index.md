# PX4 Study Docs

Generated architecture study documents for `src/modules`.

- Module documentation targets: `71`
- Scope: all immediate `src/modules/*` directories plus nested directories that declare `px4_add_module(...)`.
- Outputs: one Markdown and one standalone HTML file per target.

| Module | HTML | Build kind | Target | Topics | Classes |
| --- | --- | --- | --- | --- | --- |
| [`airship_att_control`](modules/airship_att_control.md) | [html](modules/airship_att_control.html) | px4 module | modules__airship_att_control | 6 | 1 |
| [`airspeed_selector`](modules/airspeed_selector.md) | [html](modules/airspeed_selector.html) | px4 module | modules__airspeed_selector | 18 | 3 |
| [`attitude_estimator_q`](modules/attitude_estimator_q.md) | [html](modules/attitude_estimator_q.html) | px4 module | modules__attitude_estimator_q | 10 | 1 |
| [`battery_status`](modules/battery_status.md) | [html](modules/battery_status.html) | px4 module | modules__battery_status | 2 | 2 |
| [`camera_feedback`](modules/camera_feedback.md) | [html](modules/camera_feedback.html) | px4 module | modules__camera_feedback | 5 | 1 |
| [`commander`](modules/commander.md) | [html](modules/commander.html) | px4 module | modules__commander | 78 | 95 |
| [`control_allocator`](modules/control_allocator.md) | [html](modules/control_allocator.html) | px4 module | modules__control_allocator | 21 | 25 |
| [`dataman`](modules/dataman.md) | [html](modules/dataman.html) | px4 module | modules__dataman | 3 | 0 |
| [`ekf2`](modules/ekf2.md) | [html](modules/ekf2.html) | px4 module | modules__ekf2 | 76 | 51 |
| [`esc_battery`](modules/esc_battery.md) | [html](modules/esc_battery.html) | px4 module | modules__esc_battery | 2 | 1 |
| [`events`](modules/events.md) | [html](modules/events.html) | px4 module | modules__events | 8 | 5 |
| [`flight_mode_manager`](modules/flight_mode_manager.md) | [html](modules/flight_mode_manager.html) | px4 module | modules__flight_mode_manager | 26 | 26 |
| [`fw_att_control`](modules/fw_att_control.md) | [html](modules/fw_att_control.html) | px4 module | modules__fw_att_control | 15 | 2 |
| [`fw_autotune_attitude_control`](modules/fw_autotune_attitude_control.md) | [html](modules/fw_autotune_attitude_control.html) | px4 module | fw_autotune_attitude_control | 10 | 4 |
| [`fw_lateral_longitudinal_control`](modules/fw_lateral_longitudinal_control.md) | [html](modules/fw_lateral_longitudinal_control.html) | px4 module | modules__fw_lateral_longitudinal_control | 20 | 1 |
| [`fw_mode_manager`](modules/fw_mode_manager.md) | [html](modules/fw_mode_manager.html) | px4 module | modules__fw_mode_manager | 29 | 8 |
| [`fw_rate_control`](modules/fw_rate_control.md) | [html](modules/fw_rate_control.html) | px4 module | modules__fw_rate_control | 22 | 2 |
| [`gimbal`](modules/gimbal.md) | [html](modules/gimbal.html) | px4 module | drivers__gimbal | 19 | 15 |
| [`gyro_calibration`](modules/gyro_calibration.md) | [html](modules/gyro_calibration.html) | px4 module | modules__gyro_calibration | 4 | 1 |
| [`gyro_fft`](modules/gyro_fft.md) | [html](modules/gyro_fft.html) | px4 module | modules__gyro_fft | 6 | 2 |
| [`hardfault_stream`](modules/hardfault_stream.md) | [html](modules/hardfault_stream.html) | px4 module | modules__hardfault_stream | 2 | 2 |
| [`internal_combustion_engine_control`](modules/internal_combustion_engine_control.md) | [html](modules/internal_combustion_engine_control.html) | px4 module | modules__internal_combustion_engine_control | 7 | 5 |
| [`land_detector`](modules/land_detector.md) | [html](modules/land_detector.html) | px4 module | modules__land_detector | 19 | 8 |
| [`landing_target_estimator`](modules/landing_target_estimator.md) | [html](modules/landing_target_estimator.html) | px4 module | modules__landing_target_estimator | 7 | 3 |
| [`load_mon`](modules/load_mon.md) | [html](modules/load_mon.html) | px4 module | modules__load_mon | 2 | 1 |
| [`local_position_estimator`](modules/local_position_estimator.md) | [html](modules/local_position_estimator.html) | px4 module | modules__local_position_estimator | 25 | 1 |
| [`logger`](modules/logger.md) | [html](modules/logger.html) | px4 module | modules__logger | 11 | 13 |
| [`mag_bias_estimator`](modules/mag_bias_estimator.md) | [html](modules/mag_bias_estimator.html) | px4 module | modules__mag_bias_estimator | 5 | 1 |
| [`manual_control`](modules/manual_control.md) | [html](modules/manual_control.html) | px4 module | modules__manual_control | 8 | 7 |
| [`mavlink`](modules/mavlink.md) | [html](modules/mavlink.html) | px4 module | modules__mavlink | 133 | 133 |
| [`mc_att_control`](modules/mc_att_control.md) | [html](modules/mc_att_control.html) | px4 module | modules__mc_att_control | 12 | 3 |
| [`mc_autotune_attitude_control`](modules/mc_autotune_attitude_control.md) | [html](modules/mc_autotune_attitude_control.html) | px4 module | mc_autotune_attitude_control | 9 | 2 |
| [`mc_hover_thrust_estimator`](modules/mc_hover_thrust_estimator.md) | [html](modules/mc_hover_thrust_estimator.html) | px4 module | modules__mc_hover_thrust_estimator | 8 | 3 |
| [`mc_nn_control`](modules/mc_nn_control.md) | [html](modules/mc_nn_control.html) | px4 module | mc_nn_control | 16 | 1 |
| [`mc_pos_control`](modules/mc_pos_control.md) | [html](modules/mc_pos_control.html) | px4 module | modules__mc_pos_control | 12 | 10 |
| [`mc_raptor`](modules/mc_raptor.md) | [html](modules/mc_raptor.html) | px4 module | modules__mc_raptor | 17 | 3 |
| [`mc_rate_control`](modules/mc_rate_control.md) | [html](modules/mc_rate_control.html) | px4 module | modules__mc_rate_control | 16 | 1 |
| [`muorb`](modules/muorb.md) | [html](modules/muorb.html) | directory | muorb | 0 | 5 |
| [`muorb/apps`](modules/muorb__apps.md) | [html](modules/muorb__apps.html) | px4 module | modules__muorb__apps | 0 | 2 |
| [`muorb/slpi`](modules/muorb__slpi.md) | [html](modules/muorb__slpi.html) | px4 module | modules__muorb__slpi__main | 0 | 2 |
| [`navigator`](modules/navigator.md) | [html](modules/navigator.html) | px4 module | modules__navigator | 34 | 73 |
| [`payload_deliverer`](modules/payload_deliverer.md) | [html](modules/payload_deliverer.html) | px4 module | modules__payload_deliverer | 4 | 6 |
| [`px4iofirmware`](modules/px4iofirmware.md) | [html](modules/px4iofirmware.html) | library | px4iofirmware | 1 | 0 |
| [`rc_update`](modules/rc_update.md) | [html](modules/rc_update.html) | px4 module | modules__rc_update | 7 | 3 |
| [`replay`](modules/replay.md) | [html](modules/replay.html) | px4 module | modules__replay | 24 | 7 |
| [`rover_ackermann`](modules/rover_ackermann.md) | [html](modules/rover_ackermann.html) | px4 module | modules__rover_ackermann | 23 | 9 |
| [`rover_differential`](modules/rover_differential.md) | [html](modules/rover_differential.html) | px4 module | modules__rover_differential | 21 | 10 |
| [`rover_mecanum`](modules/rover_mecanum.md) | [html](modules/rover_mecanum.html) | px4 module | modules__rover_mecanum | 21 | 9 |
| [`sensors`](modules/sensors.md) | [html](modules/sensors.html) | px4 module | modules__sensors | 39 | 21 |
| [`simulation`](modules/simulation.md) | [html](modules/simulation.html) | directory | simulation | 42 | 53 |
| [`simulation/battery_simulator`](modules/simulation__battery_simulator.md) | [html](modules/simulation__battery_simulator.html) | px4 module | modules__simulation__battery_simulator | 5 | 1 |
| [`simulation/gz_bridge`](modules/simulation__gz_bridge.md) | [html](modules/simulation__gz_bridge.html) | px4 module | modules__simulation__gz_bridge | 23 | 9 |
| [`simulation/pwm_out_sim`](modules/simulation__pwm_out_sim.md) | [html](modules/simulation__pwm_out_sim.html) | px4 module | modules__simulation__pwm_out_sim | 2 | 1 |
| [`simulation/sensor_agp_sim`](modules/simulation__sensor_agp_sim.md) | [html](modules/simulation__sensor_agp_sim.html) | px4 module | modules__simulation__sensor_agp_sim | 4 | 2 |
| [`simulation/sensor_airspeed_sim`](modules/simulation__sensor_airspeed_sim.md) | [html](modules/simulation__sensor_airspeed_sim.html) | px4 module | modules__simulation__sensor_airspeed_sim | 9 | 1 |
| [`simulation/sensor_baro_sim`](modules/simulation__sensor_baro_sim.md) | [html](modules/simulation__sensor_baro_sim.html) | px4 module | modules__simulation__sensor_baro_sim | 3 | 1 |
| [`simulation/sensor_gps_sim`](modules/simulation__sensor_gps_sim.md) | [html](modules/simulation__sensor_gps_sim.html) | px4 module | modules__simulation__sensor_gps_sim | 8 | 1 |
| [`simulation/sensor_mag_sim`](modules/simulation__sensor_mag_sim.md) | [html](modules/simulation__sensor_mag_sim.html) | px4 module | modules__simulation__senosr_mag_sim | 5 | 1 |
| [`simulation/simulator_mavlink`](modules/simulation__simulator_mavlink.md) | [html](modules/simulation__simulator_mavlink.html) | px4 module | modules__simulation__simulator_mavlink | 32 | 4 |
| [`simulation/simulator_sih`](modules/simulation__simulator_sih.md) | [html](modules/simulation__simulator_sih.html) | px4 module | modules__simulation__simulator_sih | 15 | 6 |
| [`simulation/system_power_simulator`](modules/simulation__system_power_simulator.md) | [html](modules/simulation__system_power_simulator.html) | px4 module | modules__simulation__system_power_simulator | 1 | 1 |
| [`spacecraft`](modules/spacecraft.md) | [html](modules/spacecraft.html) | px4 module | modules__spacecraft | 24 | 10 |
| [`task_watchdog`](modules/task_watchdog.md) | [html](modules/task_watchdog.html) | px4 module | modules__task_watchdog | 0 | 1 |
| [`temperature_compensation`](modules/temperature_compensation.md) | [html](modules/temperature_compensation.html) | px4 module | modules__temperature_compensation | 9 | 10 |
| [`time_persistor`](modules/time_persistor.md) | [html](modules/time_persistor.html) | px4 module | modules__time_persistor | 0 | 1 |
| [`uuv_att_control`](modules/uuv_att_control.md) | [html](modules/uuv_att_control.html) | px4 module | modules__uuv_att_control | 9 | 1 |
| [`uuv_pos_control`](modules/uuv_pos_control.md) | [html](modules/uuv_pos_control.html) | px4 module | modules__uuv_pos_control | 9 | 1 |
| [`uxrce_dds_client`](modules/uxrce_dds_client.md) | [html](modules/uxrce_dds_client.html) | px4 module | modules__uxrce_dds_client | 5 | 7 |
| [`vision_target_estimator`](modules/vision_target_estimator.md) | [html](modules/vision_target_estimator.html) | px4 module | modules__vision_target_estimator | 28 | 20 |
| [`vtol_att_control`](modules/vtol_att_control.md) | [html](modules/vtol_att_control.html) | px4 module | modules__vtol_att_control | 29 | 13 |
| [`zenoh`](modules/zenoh.md) | [html](modules/zenoh.html) | px4 module | modules__zenoh | 4 | 7 |
