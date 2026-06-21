# Ubuntu 22.04 Host Setup

This setup targets Ubuntu 22.04 Jammy with ROS 2 Humble. It assumes the host
machine is the simulator, QGroundControl, and ROS 2 development computer.

## Host Packages

Install serial and build tools:

```sh
sudo apt update
sudo apt install -y \
  build-essential \
  cmake \
  curl \
  git \
  locales \
  python3-colcon-common-extensions \
  python3-pip \
  python3-rosdep \
  python3-vcstool \
  software-properties-common
```

Allow your user to access USB serial devices:

```sh
sudo usermod -a -G dialout "$USER"
```

Log out and log back in before relying on the new group membership.

## Install ROS 2 Humble

Set a UTF-8 locale:

```sh
locale
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
locale
```

Enable the Ubuntu Universe repository and install the ROS apt source package:

```sh
sudo apt install -y software-properties-common
sudo add-apt-repository universe

sudo apt update
sudo apt install -y curl
export ROS_APT_SOURCE_VERSION="$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F tag_name | awk -F'\"' '{print $4}')"
curl -L -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
```

Update the system before installing ROS 2. This is important on fresh
Ubuntu 22.04 installs because early Jammy package states can otherwise remove
critical `systemd` or `udev` packages while resolving ROS dependencies.

```sh
sudo apt update
sudo apt upgrade -y
```

Install ROS 2. The base install is enough for this reference node:

```sh
sudo apt install -y ros-humble-ros-base ros-dev-tools
```

Source ROS 2 in new shells:

```sh
echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
source /opt/ros/humble/setup.bash
```

If `rosdep` has not been initialized on this machine:

```sh
sudo rosdep init
rosdep update
```

## Install the Micro XRCE-DDS Agent

PX4 in this tree uses the Micro XRCE-DDS v2 client path by default. Use a v2
agent for compatibility. This reference builds the agent standalone and pins
`v2.4.3`, matching PX4's standalone source-build guidance.

```sh
mkdir -p ~/src
cd ~/src
git clone -b v2.4.3 https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
cd Micro-XRCE-DDS-Agent
mkdir -p build
cd build
cmake ..
make -j"$(nproc)"
sudo make install
sudo ldconfig /usr/local/lib/
```

Verify the agent is visible:

```sh
MicroXRCEAgent --help
```

Avoid unpinned snap or distro packages for first bring-up unless you have
confirmed they provide a v2 agent compatible with the PX4 client.

If you intentionally build the agent inside a ROS 2 Humble colcon workspace
instead of standalone, check the PX4 uXRCE-DDS guide for the ROS-distro-specific
agent version mapping before choosing a branch.

## Build the Reference ROS 2 Workspace

The helper script creates `~/nucleo_px4_ros2_ws`, symlinks this package into
the workspace, clones `px4_msgs`, and builds with `colcon`:

```sh
boards/st/nucleo-h753zi/ros2_ref/scripts/build_ros2_workspace.sh
```

Manual equivalent:

```sh
mkdir -p ~/nucleo_px4_ros2_ws/src
cd ~/nucleo_px4_ros2_ws/src

git clone https://github.com/PX4/px4_msgs.git
ln -s /home/jaeheek/px4/PX4-Autopilot/boards/st/nucleo-h753zi/ros2_ref/ros2_ws/src/nucleo_px4_ros2_ref \
  nucleo_px4_ros2_ref

cd ~/nucleo_px4_ros2_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -y
colcon build --symlink-install
source install/setup.bash
```

If this PX4 checkout has local message changes, synchronize `px4_msgs` with
the messages used by the firmware build before running the node. The DDS topic
set compiled into the firmware is defined by:

```text
src/modules/uxrce_dds_client/dds_topics.yaml
```

## Start the Serial Agent

Wire USART6 through a USB-UART adapter and identify the host device:

```sh
dmesg | grep -E 'ttyUSB|ttyACM' | tail
```

Start the agent:

```sh
boards/st/nucleo-h753zi/ros2_ref/scripts/run_agent_serial.sh /dev/ttyUSB0
```

The expected connection output includes a session creation line for client key
`0x00000001` followed by topic, data writer, and data reader creation logs.

## References

- ROS 2 Humble Ubuntu deb package installation:
  `https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html`
- ROS 2 apt source package instructions:
  `https://github.com/ros2/ros2_documentation/tree/humble/source/Installation`
- PX4 uXRCE-DDS bridge documentation:
  `https://docs.px4.io/main/en/middleware/uxrce_dds`
- eProsima Micro XRCE-DDS installation manual:
  `https://micro-xrce-dds.docs.eprosima.com/en/stable/installation.html`
