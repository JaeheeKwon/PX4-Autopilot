############################################################################
#
# Copyright (c) 2026 PX4 Development Team. All rights reserved.
#
############################################################################

px4_add_module(
	MODULE systemcmds__usart6_hello
	MAIN usart6_hello
	STACK_MAIN 1800
	SRCS
		usart6_hello.cpp
)
