FROM osrf/ros:humble-desktop

# Temel bağımlılıklar ve Gazebo Fortress kütüphaneleri
RUN apt-get update && apt-get install -y \
    git python3-pip cmake build-essential \
    libignition-gazebo6-dev rapidjson-dev \
    ros-humble-ros-gz ros-humble-ros-gz-bridge \
    ros-humble-ros-gz-sim ros-humble-rqt ros-humble-rqt-image-view \
    && rm -rf /var/lib/apt/lists/*

# Python paketleri ve sürüm düzeltmeleri (empy<4, setuptools<80)
RUN pip3 install --ignore-installed "empy<4" dronecan pexpect future "setuptools<80.0.0" pymavlink

# ArduPilot SITL Kurulumu
WORKDIR /
RUN git clone https://github.com/ArduPilot/ardupilot.git
WORKDIR /ardupilot
RUN git submodule update --init --recursive --depth 1
# Root yetkisiyle kuruluma izin ver
RUN sed -i 's/exit 1/ /g' Tools/environment_install/install-prereqs-ubuntu.sh
RUN USER=root Tools/environment_install/install-prereqs-ubuntu.sh -y
RUN ./waf configure --board sitl && ./waf copter

# ardupilot_gazebo Eklentisi (Fortress dalı)
WORKDIR /
RUN git clone https://github.com/ArduPilot/ardupilot_gazebo.git
WORKDIR /ardupilot_gazebo
RUN git fetch --all && git checkout fortress
RUN mkdir build
WORKDIR /ardupilot_gazebo/build
RUN cmake .. -DCMAKE_BUILD_TYPE=Release && make -j4 && make install

# Ortam Değişkenleri
RUN echo 'export GZ_SIM_SYSTEM_PLUGIN_PATH=/ardupilot_gazebo/build:${GZ_SIM_SYSTEM_PLUGIN_PATH}' >> ~/.bashrc
RUN echo 'export GZ_SIM_RESOURCE_PATH=/ardupilot_gazebo/models:${GZ_SIM_RESOURCE_PATH}' >> ~/.bashrc
