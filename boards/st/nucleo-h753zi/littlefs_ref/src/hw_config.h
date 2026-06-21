/****************************************************************************
 * boards/st/nucleo-h753zi/src/hw_config.h
 *
 * Bootloader hardware configuration for ST Nucleo-H753ZI.
 ****************************************************************************/

#ifndef HW_CONFIG_H_
#define HW_CONFIG_H_

#define USB0_DEV       0x01
#define SERIAL0_DEV    0x02
#define SERIAL1_DEV    0x04

#define APP_LOAD_ADDRESS               0x08020000
#define BOOTLOADER_DELAY               3000
#define INTERFACE_USB                  1
#define INTERFACE_USB_CONFIG           "/dev/ttyACM0"
#define BOARD_VBUS                     MK_GPIO_INPUT(GPIO_OTGFS_VBUS)

#define BOARD_TYPE                     1210  /* matches firmware.prototype board_id */
#define BOARD_FLASH_SECTORS            (11)
#define BOARD_FLASH_SIZE               (16 * 128 * 1024)
#define APP_RESERVATION_SIZE           (4 * 128 * 1024)

#define OSC_FREQ                       8

/* Nucleo LEDs are active-HIGH pushpull (unlike most PX4 boards which are active-LOW) */
/* LED_ACTIVITY and LED_BOOTLOADER are intentionally unmapped here so that bl.c's
 * built-in 50ms blink and USB-activity toggling are no-ops. LD1 (Green, PB0) is
 * driven exclusively by the 500ms heartbeat in board_timerhook(). */
#define BOARD_LED_ON                   1
#define BOARD_LED_OFF                  0

#define SERIAL_BREAK_DETECT_DISABLED   1

#if !defined(ARCH_SN_MAX_LENGTH)
# define ARCH_SN_MAX_LENGTH 12
#endif

#if !defined(APP_RESERVATION_SIZE)
#  define APP_RESERVATION_SIZE 0
#endif

#if !defined(BOARD_FIRST_FLASH_SECTOR_TO_ERASE)
#  define BOARD_FIRST_FLASH_SECTOR_TO_ERASE 1
#endif

#if !defined(USB_DATA_ALIGN)
# define USB_DATA_ALIGN
#endif

#ifndef BOOT_DEVICES_SELECTION
#  define BOOT_DEVICES_SELECTION USB0_DEV|SERIAL0_DEV|SERIAL1_DEV
#endif

#ifndef BOOT_DEVICES_FILTER_ONUSB
#  define BOOT_DEVICES_FILTER_ONUSB USB0_DEV|SERIAL0_DEV|SERIAL1_DEV
#endif

#endif /* HW_CONFIG_H_ */
