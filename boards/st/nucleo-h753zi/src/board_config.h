/****************************************************************************
 * boards/st/nucleo-h753zi/src/board_config.h
 *
 * ST Nucleo-H753ZI internal definitions
 ****************************************************************************/

#pragma once

#include <px4_platform_common/px4_config.h>
#include <nuttx/compiler.h>
#include <stdint.h>
#include <stm32_gpio.h>

/* LEDs -- active HIGH pushpull (NOT opendrain like most PX4 boards)
 *   LD1 Green : PB0
 *   LD2 Blue  : PE1
 *   LD3 Red   : PB14
 * GPIO_OUTPUT_CLEAR = output low = OFF at boot
 */
#define GPIO_nLED_GREEN   /* PB0  */ (GPIO_OUTPUT|GPIO_PUSHPULL|GPIO_SPEED_50MHz|GPIO_OUTPUT_CLEAR|GPIO_PORTB|GPIO_PIN0)
#define GPIO_nLED_BLUE    /* PE1  */ (GPIO_OUTPUT|GPIO_PUSHPULL|GPIO_SPEED_50MHz|GPIO_OUTPUT_CLEAR|GPIO_PORTE|GPIO_PIN1)
#define GPIO_nLED_RED     /* PB14 */ (GPIO_OUTPUT|GPIO_PUSHPULL|GPIO_SPEED_50MHz|GPIO_OUTPUT_CLEAR|GPIO_PORTB|GPIO_PIN14)

#define BOARD_HAS_CONTROL_STATUS_LEDS   1
#define BOARD_OVERLOAD_LED              LED_RED
#define BOARD_ARMED_STATE_LED           LED_GREEN

/* USB OTG FS
 *   VBUS sense on PA9 (ST-LINK reports bus power)
 *   DM = PA11, DP = PA12 (fixed by STM32 USB FS hardware)
 */
#define GPIO_OTGFS_VBUS   /* PA9 */ (GPIO_INPUT|GPIO_PULLDOWN|GPIO_SPEED_100MHz|GPIO_PORTA|GPIO_PIN9)

/* High-resolution timer: TIM5 channel 1 */
#define HRT_TIMER           5
#define HRT_TIMER_CHANNEL   1

#define BOARD_DMA_ALLOC_POOL_SIZE  5120

/* No PWM output channels on this minimal board */
#define DIRECT_PWM_OUTPUT_CHANNELS  0

/* GPIO init list */
#define PX4_GPIO_INIT_LIST { \
		GPIO_OTGFS_VBUS,    \
	}

#define BOARD_ENABLE_CONSOLE_BUFFER

/* File-backed params are stored on LittleFS mounted by board_app_initialize(). */

__BEGIN_DECLS
extern void stm32_usbinitialize(void);
#include <px4_platform_common/board_common.h>
__END_DECLS
