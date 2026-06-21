/****************************************************************************
 * boards/st/nucleo-h753zi/src/init.c
 *
 * PX4 board init for ST Nucleo-H753ZI.
 * Minimal: LEDs, USB, DMA pool, flash-based params.
 ****************************************************************************/

#include <arch/board/board.h>
#include <chip.h>
#include <debug.h>
#include <drivers/drv_board_led.h>
#include <drivers/drv_hrt.h>
#include <errno.h>
#include <fcntl.h>
#include <mpu.h>
#include <nuttx/board.h>
#include <nuttx/config.h>
#include <nuttx/mtd/mtd.h>
#include <px4_arch/io_timer.h>
#include <px4_platform/board_dma_alloc.h>
#include <px4_platform/gpio.h>
#include <px4_platform_common/init.h>
#include <stdbool.h>
#include <stdio.h>
#include <stm32_uart.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <syslog.h>
#include <systemlib/px4_macros.h>

#include "arm_internal.h"
#include "board_config.h"

#if defined(FLASH_BASED_PARAMS)
#include <parameters/flashparams/flashfs.h>
#endif

__BEGIN_DECLS
extern void led_init(void);
extern void led_on(int led);
extern void led_off(int led);
__END_DECLS

/* LD2 (Blue, PE1) heartbeat: 500ms toggle to indicate the application is
 * running. */
static struct hrt_call _led2_call;

static void led2_heartbeat(void* arg) {
	stm32_gpiowrite(GPIO_nLED_BLUE, stm32_gpioread(GPIO_nLED_BLUE) ^ 1);
	hrt_call_after(&_led2_call, 500000, led2_heartbeat, NULL);
}

__EXPORT void board_peripheral_reset(int ms) {}

__EXPORT void board_on_reset(int status) {}

/* Required when CONFIG_SYSTEMTICK_HOOK=y; bootloader_main.c provides the real
 * one. */
void __attribute__((weak)) board_timerhook(void) {}

__EXPORT void stm32_boardinitialize(void) {
	board_autoled_initialize();

	const uint32_t gpio[] = PX4_GPIO_INIT_LIST;
	px4_gpio_init(gpio, arraySize(gpio));

	stm32_usbinitialize();
}

__EXPORT int board_app_initialize(uintptr_t arg) {
	px4_platform_init();

	if (board_dma_alloc_init() < 0) {
		syslog(LOG_ERR, "[boot] DMA alloc FAILED\n");
	}

	drv_led_start();
	led_off(LED_RED);
	led_off(LED_GREEN);
	led_off(LED_BLUE);

	/* Start LD2 (Blue, PE1) 500ms heartbeat — indicates application is
	 * running. */
	hrt_call_after(&_led2_call, 500000, led2_heartbeat, NULL);

	if (board_hardfault_init(2, true) != 0) {
		led_on(LED_RED);
	}

#if defined(FLASH_BASED_PARAMS)
	/* Last two 128 KB sectors of Bank 2: sectors 14 and 15 */
	static sector_descriptor_t params_sector_map[] = {
	    {14, 128 * 1024, 0x081C0000},
	    {15, 128 * 1024, 0x081E0000},
	    {0, 0, 0},
	};
	// paramfs is not a file system but use the flash memory for parameter
	// storage thus it's not visiable via filesystem api. no not shown by
	// ls command.
	int result = parameter_flashfs_init(params_sector_map, NULL, 0);

	if (result != OK) {
		syslog(LOG_ERR, "[boot] FAILED to init params in FLASH %d\n",
		       result);
		led_on(LED_RED);
	}

#endif

	px4_platform_configure();

	return OK;
}
