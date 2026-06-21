/****************************************************************************
 * boards/st/nucleo-h753zi/src/init.c
 *
 * PX4 board init for ST Nucleo-H753ZI.
 * Minimal: LEDs, USB, DMA pool, LittleFS-backed params.
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
#include <nuttx/fs/fs.h>
#include <nuttx/mtd/mtd.h>
#include <px4_arch/io_timer.h>
#include <px4_platform/board_dma_alloc.h>
#include <px4_platform/gpio.h>
#include <px4_platform_common/init.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stm32_uart.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <syslog.h>
#include <systemlib/px4_macros.h>
#include <unistd.h>

#include "arm_internal.h"
#include "board_config.h"

__BEGIN_DECLS
extern void led_init(void);
extern void led_on(int led);
extern void led_off(int led);
__END_DECLS

#define PARAM_LITTLEFS_DEVICE       "/dev/mtd_params"
#define PARAM_LITTLEFS_MOUNTPOINT   "/fs/flash"
#define PARAM_LITTLEFS_ERASE_BLOCKS 4
#define PARAM_LITTLEFS_TEST_FILE    PARAM_LITTLEFS_MOUNTPOINT "/.mount_test"

static int mount_parameter_littlefs(void)
{
	struct mtd_dev_s *progmem = progmem_initialize();

	if (progmem == NULL) {
		syslog(LOG_ERR, "[boot] progmem_initialize failed\n");
		return -ENODEV;
	}

	struct mtd_geometry_s geo;
	memset(&geo, 0, sizeof(geo));

	int ret = progmem->ioctl(progmem, MTDIOC_GEOMETRY,
				 (unsigned long)((uintptr_t)&geo));

	if (ret < 0) {
		syslog(LOG_ERR, "[boot] progmem geometry failed: %d\n", ret);
		return ret;
	}

	if (geo.blocksize == 0 || geo.erasesize == 0 ||
	    geo.neraseblocks < PARAM_LITTLEFS_ERASE_BLOCKS ||
	    (geo.erasesize % geo.blocksize) != 0) {
		syslog(LOG_ERR,
		       "[boot] invalid progmem geometry: block=%lu erase=%lu n=%lu\n",
		       (unsigned long)geo.blocksize,
		       (unsigned long)geo.erasesize,
		       (unsigned long)geo.neraseblocks);
		return -EINVAL;
	}

	const off_t blocks_per_erase = geo.erasesize / geo.blocksize;
	const off_t first_block = (geo.neraseblocks - PARAM_LITTLEFS_ERASE_BLOCKS) *
				  blocks_per_erase;
	const off_t block_count = PARAM_LITTLEFS_ERASE_BLOCKS * blocks_per_erase;

	struct mtd_dev_s *params_mtd = mtd_partition(progmem, first_block,
				    block_count);

	if (params_mtd == NULL) {
		syslog(LOG_ERR,
		       "[boot] failed to create param MTD partition at erase block %lu\n",
		       (unsigned long)(geo.neraseblocks - PARAM_LITTLEFS_ERASE_BLOCKS));
		return -ENODEV;
	}

	ret = register_mtddriver(PARAM_LITTLEFS_DEVICE, params_mtd, 0755, NULL);

	if (ret < 0 && ret != -EEXIST) {
		syslog(LOG_ERR, "[boot] register %s failed: %d\n",
		       PARAM_LITTLEFS_DEVICE, ret);
		return ret;
	}

	ret = mkdir("/fs", 0777);

	if (ret < 0 && errno != EEXIST) {
		syslog(LOG_ERR, "[boot] mkdir /fs failed: %d\n", errno);
		return -errno;
	}

	ret = mkdir(PARAM_LITTLEFS_MOUNTPOINT, 0777);

	if (ret < 0 && errno != EEXIST) {
		syslog(LOG_ERR, "[boot] mkdir %s failed: %d\n",
		       PARAM_LITTLEFS_MOUNTPOINT, errno);
		return -errno;
	}

	ret = nx_mount(PARAM_LITTLEFS_DEVICE, PARAM_LITTLEFS_MOUNTPOINT,
		       "littlefs", 0, "autoformat");

	if (ret < 0) {
		syslog(LOG_ERR, "[boot] mount LittleFS params failed: %d\n", ret);
		return ret;
	}

	int fd = open(PARAM_LITTLEFS_TEST_FILE, O_CREAT | O_WRONLY | O_TRUNC, 0600);

	if (fd < 0) {
		ret = -errno;
		syslog(LOG_ERR, "[boot] LittleFS mount is not writable: %d\n", errno);
		return ret;
	}

	close(fd);
	unlink(PARAM_LITTLEFS_TEST_FILE);
	syslog(LOG_INFO, "[boot] LittleFS params mounted at %s\n",
	       PARAM_LITTLEFS_MOUNTPOINT);
	return OK;
}

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

	/* Start LD2 (Blue, PE1) 500ms heartbeat - indicates application is
	 * running. */
	hrt_call_after(&_led2_call, 500000, led2_heartbeat, NULL);

	if (board_hardfault_init(2, true) != 0) {
		led_on(LED_RED);
	}

	if (mount_parameter_littlefs() != OK) {
		led_on(LED_RED);
	}

	px4_platform_configure();

	return OK;
}
