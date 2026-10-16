from pymavlink import mavutil
import time

print("SITL'e (UDP 14550) bağlanılıyor...")
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()
print("Bağlantı başarılı! İHA ile iletişim kuruldu.")

# GUIDED Moda Al
master.mav.set_mode_send(
    master.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 4)
print("GUIDED moduna geçildi.")
time.sleep(1)

# Motorları Arm Et (Çalıştır)
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
print("Motorlar Arm edildi.")
time.sleep(2)

# 10 Metreye Kalkış (Takeoff)
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 10)
print("Kalkış yapılıyor (10 metre)...")
time.sleep(10) # Yükselmesi için süre tanı

# 4 Noktalı NED Uçuş Fonksiyonu (Kuzey, Doğu, Aşağı)
def goto_ned(x, y, z):
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, 0b0000111111111000,
        x, y, z, 0, 0, 0, 0, 0, 0, 0, 0)
    print(f"Hedefe gidiliyor: Kuzey={x}m, Doğu={y}m, Yükseklik={-z}m")
    time.sleep(8) # Noktaya ulaşması için süre tanı

# NED Sisteminde Z ekseni aşağıyı gösterir, bu yüzden yükseklik negatiftir (-10)
goto_ned(15, 0, -10)   # 1. Nokta: 15m İleri
goto_ned(15, 15, -10)  # 2. Nokta: 15m Sağa
goto_ned(0, 15, -10)   # 3. Nokta: 15m Geri
goto_ned(0, 0, -10)    # 4. Nokta: Başlangıç Noktasına Dönüş

# İniş (LAND Modu)
master.mav.set_mode_send(
    master.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 9)
print("Görev tamamlandı. İniş (LAND) yapılıyor...")
