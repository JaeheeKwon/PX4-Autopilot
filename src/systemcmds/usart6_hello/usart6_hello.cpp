/****************************************************************************
 *
 * Copyright (c) 2026 PX4 Development Team. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name PX4 nor the names of its contributors may be used
 *    to endorse or promote products derived from this software without
 *    specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED.
 *
 ****************************************************************************/

#include <px4_platform_common/getopt.h>
#include <px4_platform_common/log.h>
#include <px4_platform_common/module.h>

#include <drivers/drv_hrt.h>

#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <poll.h>
#include <termios.h>
#include <unistd.h>

#ifndef B460800
#define B460800 460800
#endif

#ifndef B921600
#define B921600 921600
#endif

static void print_usage()
{
	PRINT_MODULE_DESCRIPTION(
		"Send a periodic hello message on a UART and echo received bytes.\n"
		"Stop any module using the selected device before running this test.\n"
		"The command returns 0 after receiving at least one byte, or 2 if the\n"
		"transmit-only timeout expires without receiving host data.");
	PRINT_MODULE_USAGE_NAME("usart6_hello", "command");
	PRINT_MODULE_USAGE_PARAM_STRING('d', "/dev/ttyS1", "<device>", "UART device", true);
	PRINT_MODULE_USAGE_PARAM_INT('b', 921600, 57600, 921600, "Baud rate", true);
	PRINT_MODULE_USAGE_PARAM_INT('t', 30, 1, 600, "Test duration in seconds", true);
	PRINT_MODULE_USAGE_PARAM_INT('i', 1000, 100, 10000, "Hello interval in milliseconds", true);
}

static speed_t baud_to_speed(int baud)
{
	switch (baud) {
	case 57600:  return B57600;
	case 115200: return B115200;
	case 230400: return B230400;
	case 460800: return B460800;
	case 921600: return B921600;
	default:     return 0;
	}
}

static int configure_uart(int fd, int baud, termios &original)
{
	if (tcgetattr(fd, &original) < 0) {
		PX4_ERR("tcgetattr failed: %d", errno);
		return -1;
	}

	termios config = original;
	config.c_iflag &= ~(IGNBRK | BRKINT | ICRNL | INLCR | PARMRK | INPCK |
			   ISTRIP | IXON | IXOFF | IXANY);
	config.c_oflag = 0;
	config.c_lflag &= ~(ECHO | ECHONL | ICANON | IEXTEN | ISIG);
	config.c_cflag &= ~(CSIZE | CSTOPB | PARENB | CRTSCTS);
	config.c_cflag |= (CS8 | CLOCAL | CREAD);
	config.c_cc[VMIN] = 0;
	config.c_cc[VTIME] = 0;

	const speed_t speed = baud_to_speed(baud);

	if (speed == 0) {
		PX4_ERR("unsupported baud: %d", baud);
		return -1;
	}

	if (cfsetispeed(&config, speed) < 0 || cfsetospeed(&config, speed) < 0) {
		PX4_ERR("failed to set baud %d: %d", baud, errno);
		return -1;
	}

	if (tcsetattr(fd, TCSANOW, &config) < 0) {
		PX4_ERR("tcsetattr failed: %d", errno);
		return -1;
	}

	tcflush(fd, TCIOFLUSH);
	return 0;
}

static bool write_all(int fd, const char *data, size_t length)
{
	size_t offset = 0;

	while (offset < length) {
		const ssize_t written = write(fd, data + offset, length - offset);

		if (written > 0) {
			offset += static_cast<size_t>(written);

		} else if (written < 0 && (errno == EAGAIN || errno == EINTR)) {
			pollfd output_poll{fd, POLLOUT, 0};

			if (poll(&output_poll, 1, 100) < 0 && errno != EINTR) {
				return false;
			}

		} else {
			return false;
		}
	}

	return true;
}

extern "C" __EXPORT int usart6_hello_main(int argc, char *argv[])
{
	const char *device = "/dev/ttyS1";
	int baud = 921600;
	int duration_s = 30;
	int interval_ms = 1000;
	int myoptind = 1;
	const char *myoptarg = nullptr;
	int option;

	while ((option = px4_getopt(argc, argv, "d:b:t:i:h", &myoptind, &myoptarg)) != EOF) {
		switch (option) {
		case 'd':
			device = myoptarg;
			break;

		case 'b':
			baud = static_cast<int>(strtol(myoptarg, nullptr, 10));
			break;

		case 't':
			duration_s = static_cast<int>(strtol(myoptarg, nullptr, 10));
			break;

		case 'i':
			interval_ms = static_cast<int>(strtol(myoptarg, nullptr, 10));
			break;

		case 'h':
		default:
			print_usage();
			return (option == 'h') ? 0 : 1;
		}
	}

	if (baud_to_speed(baud) == 0 || duration_s < 1 || duration_s > 600 ||
	    interval_ms < 100 || interval_ms > 10000) {
		print_usage();
		return 1;
	}

	const int fd = open(device, O_RDWR | O_NOCTTY | O_NONBLOCK);

	if (fd < 0) {
		PX4_ERR("open %s failed: %d", device, errno);
		PX4_ERR("stop uxrce_dds_client or any other owner first");
		return 1;
	}

	termios original{};

	if (configure_uart(fd, baud, original) != 0) {
		close(fd);
		return 1;
	}

	char banner[220];
	const int banner_length = snprintf(banner, sizeof(banner),
					  "\r\nPX4 USART6 HELLO\r\n"
					  "device=%s baud=%d format=8N1 flow=none\r\n"
					  "Type characters in minicom; PX4 reports each received byte.\r\n",
					  device, baud);

	if (banner_length <= 0 || banner_length >= static_cast<int>(sizeof(banner)) ||
	    !write_all(fd, banner, static_cast<size_t>(banner_length))) {
		PX4_ERR("initial UART write failed: %d", errno);
		tcsetattr(fd, TCSANOW, &original);
		close(fd);
		return 1;
	}

	PX4_INFO("testing %s at %d baud for %d seconds", device, baud, duration_s);
	PX4_INFO("type at least one character in host minicom");

	const hrt_abstime start = hrt_absolute_time();
	const hrt_abstime finish = start + static_cast<hrt_abstime>(duration_s) * 1000000ULL;
	hrt_abstime next_hello = start;
	unsigned hello_sequence = 0;
	unsigned received_count = 0;
	unsigned transmitted_count = static_cast<unsigned>(banner_length);

	while (hrt_absolute_time() < finish) {
		const hrt_abstime now = hrt_absolute_time();

		if (now >= next_hello) {
			char hello[96];
			const int length = snprintf(hello, sizeof(hello),
						    "PX4 hello #%u uptime_us=%llu\r\n",
						    hello_sequence++,
						    static_cast<unsigned long long>(now));

			if (length > 0 && write_all(fd, hello, static_cast<size_t>(length))) {
				transmitted_count += static_cast<unsigned>(length);

			} else {
				PX4_ERR("periodic UART write failed: %d", errno);
				break;
			}

			next_hello = now + static_cast<hrt_abstime>(interval_ms) * 1000ULL;
		}

		pollfd input_poll{fd, POLLIN, 0};
		const int poll_result = poll(&input_poll, 1, 50);

		if (poll_result > 0 && (input_poll.revents & POLLIN)) {
			uint8_t bytes[32];
			const ssize_t count = read(fd, bytes, sizeof(bytes));

			for (ssize_t index = 0; index < count; ++index) {
				const uint8_t byte = bytes[index];
				const char printable = (byte >= 32 && byte <= 126) ? static_cast<char>(byte) : '.';
				char response[64];
				const int length = snprintf(response, sizeof(response),
							    "PX4 RX 0x%02X '%c'\r\n",
							    static_cast<unsigned>(byte), printable);

				if (length > 0 && write_all(fd, response, static_cast<size_t>(length))) {
					transmitted_count += static_cast<unsigned>(length);
				}

				++received_count;
			}

		} else if (poll_result < 0 && errno != EINTR) {
			PX4_ERR("poll failed: %d", errno);
			break;
		}
	}

	char summary[128];
	const int summary_length = snprintf(summary, sizeof(summary),
					    "PX4 USART6 TEST %s rx_bytes=%u tx_bytes=%u\r\n",
					    received_count > 0 ? "PASS" : "TX-ONLY",
					    received_count, transmitted_count);

	if (summary_length > 0) {
		write_all(fd, summary, static_cast<size_t>(summary_length));
	}

	tcdrain(fd);
	tcsetattr(fd, TCSANOW, &original);
	close(fd);

	if (received_count == 0) {
		PX4_WARN("TX completed, but no host bytes were received");
		return 2;
	}

	PX4_INFO("PASS: USART TX and RX worked (%u received bytes)", received_count);
	return 0;
}
