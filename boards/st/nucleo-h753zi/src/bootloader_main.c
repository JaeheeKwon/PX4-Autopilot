/****************************************************************************
 * boards/st/nucleo-h753zi/src/bootloader_main.c
 *
 * Early startup code for the PX4 bootloader on ST Nucleo-H753ZI.
 ****************************************************************************/

#include "board_config.h"
#include "bl.h"

#include <nuttx/config.h>
#include <nuttx/board.h>
#include <chip.h>
#include <stm32_uart.h>
#include <arch/board/board.h>
#include "arm_internal.h"
#include <px4_platform_common/init.h>

extern int sercon_main(int c, char **argv);

/* Stubs for NuttX features that are compiled in but unused by the bootloader */

/* CROMFS image — not used in bootloader; mount will simply fail if attempted */
const uint8_t g_cromfs_image[1] = {0};

/* perf_count — called by board_dma_alloc which px4_layer pulls in */
struct perf_counter_s;
void perf_count(struct perf_counter_s *handle) { (void)handle; }

__EXPORT void board_on_reset(int status) {}

__EXPORT void stm32_boardinitialize(void)
{
	/* LD1 (Green, PB0): sole LED visible during bootloader; toggled at 500ms by board_timerhook. */
	stm32_configgpio(GPIO_nLED_GREEN);
	stm32_gpiowrite(GPIO_nLED_GREEN, 0);   /* off at start */

	stm32_usbinitialize();
}

__EXPORT int board_app_initialize(uintptr_t arg)
{
	return 0;
}

void board_late_initialize(void)
{
	sercon_main(0, NULL);
}

extern void sys_tick_handler(void);
void board_timerhook(void)
{
	sys_tick_handler();

	/* Toggle LD1 (Green, PB0) every 500ms to indicate the bootloader is running.
	 * sys_tick fires every 1ms, so count 500 ticks per half-period. */
	static unsigned ms = 0;
	static bool led_state = false;

	if (++ms >= 500) {
		ms = 0;
		led_state = !led_state;
		stm32_gpiowrite(GPIO_nLED_GREEN, led_state ? 1 : 0);
	}
}
