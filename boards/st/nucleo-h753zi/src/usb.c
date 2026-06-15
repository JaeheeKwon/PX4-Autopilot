/****************************************************************************
 * boards/st/nucleo-h753zi/src/usb.c
 *
 * USB OTG FS init. VBUS on PA9. DM/DP on PA11/PA12 (fixed by hardware).
 ****************************************************************************/

#include <nuttx/config.h>
#include "board_config.h"
#include <nuttx/usb/usbdev.h>
#include <debug.h>
#include "chip.h"
#include "stm32_gpio.h"

#ifdef CONFIG_STM32H7_OTGFS
__EXPORT void stm32_usbinitialize(void)
{
	stm32_configgpio(GPIO_OTGFS_VBUS);
}
#else
__EXPORT void stm32_usbinitialize(void) {}
#endif

__EXPORT void stm32_usbsuspend(FAR struct usbdev_s *dev, bool resume)
{
	uinfo("resume: %d\n", resume);
}
