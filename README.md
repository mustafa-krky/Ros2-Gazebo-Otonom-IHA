# Gazebo & ROS 2 İHA Otonom Simülasyonu

Bu depo, Ubuntu üzerinde Docker kullanılarak izole edilmiş bir ROS 2 (Humble) ve Gazebo (Fortress) simülasyon ortamını içerir. Projenin temel amacı, ArduPilot SITL kullanılarak döner kanatlı bir İHA'nın 4 noktalı otonom görev uçuşunu gerçekleştirmek ve otonom seyir sırasında İHA üzerindeki sanal kamera görüntüsünü `ros_gz_image` ile ROS 2 sistemine aktarmaktır.

## Özellikler ve Kullanılan Teknolojiler
* **İşletim Sistemi:** Ubuntu (Host) / Ubuntu 22.04 (Docker İçi)
* **Simülatör & Otopilot:** Gazebo Fortress, ArduPilot SITL, ardupilot_gazebo eklentisi
* **İletişim & Otonomi:** ROS 2 Humble, MAVLink (pymavlink), ros_gz_bridge

---

## Kurulum (Aşama 1 - Docker Ortamı)

Tüm bağımlılıklar, derleme kütüphaneleri ve ROS 2 ortamı `docker/Dockerfile` içerisine entegre edilmiştir. Sistemi manuel kurmak yerine tek seferde ayağa kaldırabilirsiniz.

### 1. Depoyu Klonlayın

    git clone [https://github.com/mustafa-krky/Ros2-Gazebo-Otonom-IHA.git](https://github.com/mustafa-krky/Ros2-Gazebo-Otonom-IHA.git)
    cd Ros2-Gazebo-Otonom-IHA

### 2. Docker İmajını İnşa Edin

    docker build -t iha_sim_env -f docker/Dockerfile .

### 3. Konteyneri Başlatın (GUI Destekli)

Gazebo ve rqt_image_view arayüzlerinin ekranınızda açılabilmesi için X11 yönlendirmesiyle konteyneri başlatın:

    xhost +local:root
    docker run -it --privileged \
      --env="DISPLAY=$DISPLAY" \
      --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
      --network host \
      iha_sim_env bash

---

## Yapılandırma (Aşama 2 - Konteyner İçi Hazırlık)

Konteynerin içine girdikten sonra, ortam değişkenlerini ayarlamalı ve kamera sensörünü modele eklemelisiniz.

### 1. ROS 2 Ortamını Aktif Edin ve Klasöre Geçin

Her yeni terminal açtığınızda ROS 2'yi aktif etmeniz gerekir:

    source /opt/ros/humble/setup.bash
    cd /ardupilot_gazebo

### 2. İHA Modeline Kamera Sensörü Ekleyin (Önemli!)

Varsayılan İHA modelinde (iris_with_standoffs) kamera sensörü bulunmaz. Uçuş öncesi modele sanal kamera ve render eklentisi eklenmelidir.
`nano models/iris_with_standoffs/model.sdf` komutuyla dosyayı açın:

1. `<sensor name="imu_sensor"...>` bloğunun bittiği `</sensor>` etiketi ile ana gövdenin bittiği `</link>` etiketi arasına şu kamera kodunu ekleyin:

        <sensor name="camera" type="camera">
          <pose>0.15 0 0.05 0 0 0</pose>
          <always_on>1</always_on>
          <update_rate>30.0</update_rate>
          <camera>
            <horizontal_fov>1.047</horizontal_fov>
            <image>
              <width>640</width>
              <height>480</height>
              <format>R8G8B8</format>
            </image>
            <clip>
              <near>0.1</near>
              <far>100</far>
            </clip>
          </camera>
          <topic>/camera/image_raw</topic>
        </sensor>

2. Dosyanın en altındaki `</model>` etiketinin hemen üstüne, görüntünün render edilebilmesi için şu eklentiyi ekleyip kaydedin:

        <plugin filename="libignition-gazebo-sensors-system.so" name="ignition::gazebo::systems::Sensors">
          <render_engine>ogre2</render_engine>
        </plugin>

---

## Çalıştırma Talimatları (Aşama 3 - Simülasyon ve Uçuş)

Aşağıdaki komutları konteyner içinde **5 ayrı terminal sekmesi** açarak sırasıyla çalıştırın. (Her yeni sekmede `docker exec -it $(docker ps -q -l) bash` ile konteynere girip `source /opt/ros/humble/setup.bash` komutunu girmeyi unutmayın).

**1. Simülasyon Ortamını Başlatma**

    ign gazebo -r worlds/iris_arducopter_runway.world

**2. Otopilot (SITL) Bağlantısını Kurma**

    sim_vehicle.py -v ArduCopter -f json --console
*(Güvenlik kontrollerini atlamak isterseniz açılan konsola `param set ARMING_CHECK 0` yazabilirsiniz).*

**3. Görüntü Köprüsünü (Image Bridge) Çalıştırma**

    ros2 run ros_gz_image image_bridge /camera/image_raw

**4. Kamera Arayüzünü Açma**

    ros2 run rqt_image_view rqt_image_view
*(Uygulama açıldığında sol üstteki menüden /camera/image_raw konusunu seçin ve Gazebo'da sol alttaki turuncu Play butonuna basarak simülasyon zamanını akıtmaya başlayın).*

**5. Otonom Görevi Başlatma**

    python3 otonom_ucus.py

---

## Otonom Uçuş Algoritması (otonom_ucus.py)

Projede yer alan Python betiği, İHA'nın kontrolünü sağlamak için MAVLink protokolü (pymavlink/dronekit) üzerinden otopilot ile haberleşir. 

**Çalışma Mantığı:**
1. **Bağlantı:** Sistem, UDP 14550 portu üzerinden Gazebo'da koşan SITL otopilotuna bağlanır.
2. **Kalkış:** İHA GUIDED moduna alınır, motorlar arm edilir ve simple_takeoff komutu ile 10 metre irtifaya yükselir.
3. **Seyrüsefer:** Araç sırasıyla yerel koordinat düzleminde (Kuzey, Doğu, Aşağı - NED) belirlenmiş olan kare şeklindeki hedef noktalarına ilerler. (Örn: 15m Kuzey, 15m Doğu).
4. **İniş (LAND):** Görev noktaları tamamlandığında araç otonom olarak iniş moduna geçer ve motorları kapatır.

---

## Karşılaşılan Sorunlar ve Çözüm Notları
* **Görüntü Aktarım Köprüsü (Bridge) Uyuşmazlığı:** Başlangıçta kullanılan genel parameter_bridge, Ignition ve ROS 2 arasındaki mesaj tiplerinin uyuşmazlığı nedeniyle kilitlenmiştir. Çözüm olarak sadece resim verilerine özel ros_gz_image image_bridge paketi kullanılmıştır.
* **Gri Ekran Sorunu:** Dronun kamerasının çok aşağıda kalması ve Gazebo simülasyon zamanının duraklatılmış (paused) olarak başlaması nedeniyle görüntü alınamamıştır. Çözüm olarak model SDF dosyasına Sensors eklentisi eklenmiş ve Gazebo'da simülasyon başlatılarak (Play) çözülmüştür.#
