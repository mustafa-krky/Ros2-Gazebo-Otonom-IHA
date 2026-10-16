# Gazebo & ROS 2 İHA Otonom Simülasyonu

Bu depo, Ubuntu üzerinde Docker kullanılarak izole edilmiş bir ROS 2 (Humble) ve Gazebo (Fortress) simülasyon ortamını içerir. Projenin temel amacı, ArduPilot SITL kullanılarak döner kanatlı bir İHA'nın 4 noktalı otonom görev uçuşunu gerçekleştirmek ve otonom seyir sırasında İHA üzerindeki sanal kamera görüntüsünü `ros_gz_bridge` ile ROS 2 sistemine aktarmaktır.

## Özellikler ve Kullanılan Teknolojiler
* **İşletim Sistemi:** Ubuntu (Host) / Ubuntu 22.04 (Docker İçi)
* **Simülatör & Otopilot:** Gazebo Fortress, ArduPilot SITL, ardupilot_gazebo eklentisi
* **İletişim & Otonomi:** ROS 2 Humble, MAVLink (pymavlink), ros_gz_bridge

## Kurulum (Aşama 1 - Docker Ortamı)

Tüm bağımlılıklar, derleme kütüphaneleri ve ROS 2 ortamı `docker/Dockerfile` içerisine entegre edilmiştir. Sistemi manuel kurmak yerine tek seferde ayağa kaldırabilirsiniz.

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/mustafa-krky/Ros2-Gazebo-Otonom-IHA.git
cd Ros2-Gazebo-Otonom-IHA
```

### 2. Docker İmajını İnşa Edin
```bash
docker build -t iha_sim_env -f docker/Dockerfile .
```

### 3. Konteyneri Başlatın (GUI Destekli)
Gazebo ve `rqt_image_view` arayüzlerinin ekranınızda açılabilmesi için X11 yönlendirmesiyle konteyneri başlatın:
```bash
xhost +local:root
docker run -it --privileged \
  --env="DISPLAY=$DISPLAY" \
  --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
  --network host \
  iha_sim_env bash
```
