/****************************************************************************
 * boards/st/nucleo-h753zi/src/spi.cpp
 * SPI3 is available on the Arduino shield connector (PB3/PB4/PB5).
 * No devices are attached in the default configuration.
 ****************************************************************************/

#include <px4_arch/spi_hw_description.h>
#include <drivers/drv_sensor.h>
#include <nuttx/spi/spi.h>

constexpr px4_spi_bus_t px4_spi_buses[SPI_BUS_MAX_BUS_ITEMS] = {
	initSPIBus(SPI::Bus::SPI3, {}),
};

static constexpr bool unused = validateSPIConfig(px4_spi_buses);
