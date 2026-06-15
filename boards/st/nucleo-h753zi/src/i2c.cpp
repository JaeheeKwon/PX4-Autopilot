/****************************************************************************
 * boards/st/nucleo-h753zi/src/i2c.cpp
 * No I2C-connected devices in this minimal configuration.
 ****************************************************************************/

#include <px4_arch/i2c_hw_description.h>

constexpr px4_i2c_bus_t px4_i2c_buses[I2C_BUS_MAX_BUS_ITEMS] = {};
