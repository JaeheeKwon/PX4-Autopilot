/****************************************************************************
 * boards/st/nucleo-h753zi/src/led.c
 *
 * LED driver for ST Nucleo-H753ZI.
 * All three LEDs are active HIGH (pushpull), unlike most PX4 boards.
 ****************************************************************************/

#include <px4_platform_common/px4_config.h>
#include <stdbool.h>
#include "chip.h"
#include "stm32_gpio.h"
#include "board_config.h"
#include <nuttx/board.h>
#include <arch/board/board.h>

__BEGIN_DECLS
extern void led_init(void);
extern void led_on(int led);
extern void led_off(int led);
extern void led_toggle(int led);
__END_DECLS

/* g_ledmap indexed by PX4 LED constants: LED_BLUE=0, LED_RED=1, LED_GREEN=3.
 * Index 2 is unused (no LED_AMBER hardware on Nucleo).
 */
static uint32_t g_ledmap[] = {
	GPIO_nLED_BLUE,   /* 0 -- LED_BLUE  */
	GPIO_nLED_RED,    /* 1 -- LED_RED   */
	0,                /* 2 -- unused    */
	GPIO_nLED_GREEN,  /* 3 -- LED_GREEN */
};

__EXPORT void led_init(void)
{
	for (size_t l = 0; l < (sizeof(g_ledmap) / sizeof(g_ledmap[0])); l++) {
		if (g_ledmap[l] != 0) {
			stm32_configgpio(g_ledmap[l]);
		}
	}
}

/* Active HIGH: write state directly (1=ON, 0=OFF). No inversion. */
static void phy_set_led(int led, bool state)
{
	if ((size_t)led < sizeof(g_ledmap) / sizeof(g_ledmap[0]) && g_ledmap[led] != 0) {
		stm32_gpiowrite(g_ledmap[led], state);
	}
}

static bool phy_get_led(int led)
{
	if ((size_t)led < sizeof(g_ledmap) / sizeof(g_ledmap[0]) && g_ledmap[led] != 0) {
		return stm32_gpioread(g_ledmap[led]);
	}

	return false;
}

__EXPORT void led_on(int led)      { phy_set_led(led, true);  }
__EXPORT void led_off(int led)     { phy_set_led(led, false); }
__EXPORT void led_toggle(int led)  { phy_set_led(led, !phy_get_led(led)); }

#ifdef CONFIG_ARCH_LEDS
void board_autoled_initialize(void) { led_init(); }

void board_autoled_on(int led)
{
	switch (led) {
	case LED_HEAPALLOCATE:  phy_set_led(BOARD_LED_BLUE,  true);  break;

	case LED_IRQSENABLED:   phy_set_led(BOARD_LED_GREEN, true);  break;

	case LED_STACKCREATED:  phy_set_led(BOARD_LED_GREEN, true);
		phy_set_led(BOARD_LED_BLUE,  true);  break;

	case LED_INIRQ:         phy_set_led(BOARD_LED_BLUE,  true);  break;

	case LED_SIGNAL:        phy_set_led(BOARD_LED_GREEN, true);  break;

	case LED_ASSERTION:     phy_set_led(BOARD_LED_RED,   true);  break;

	case LED_PANIC:         phy_set_led(BOARD_LED_RED,   true);  break;

	case LED_IDLE:          phy_set_led(BOARD_LED_RED,   true);  break;

	default:
		break;
	}
}

void board_autoled_off(int led)
{
	switch (led) {
	case LED_IRQSENABLED:   phy_set_led(BOARD_LED_GREEN, false); break;

	case LED_INIRQ:         phy_set_led(BOARD_LED_BLUE,  false); break;

	case LED_SIGNAL:        phy_set_led(BOARD_LED_GREEN, false); break;

	case LED_ASSERTION:     phy_set_led(BOARD_LED_RED,   false); break;

	case LED_PANIC:         phy_set_led(BOARD_LED_RED,   false); break;

	case LED_IDLE:          phy_set_led(BOARD_LED_RED,   false); break;

	default:
		break;
	}
}
#endif /* CONFIG_ARCH_LEDS */
