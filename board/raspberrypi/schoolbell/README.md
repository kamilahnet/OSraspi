# School Bell (RPi2 + Buildroot)

Konfigurasi ini menyiapkan image Buildroot untuk bel sekolah berbasis Raspberry Pi 2 dengan output audio/HDMI serta aplikasi Python yang otomatis berjalan saat boot.

## Cara Build

```sh
make raspberrypi2_schoolbell_defconfig
make
```

Hasil image SD card berada di `output/images/sdcard.img`.

## SSH & WinSCP

Layanan SSH disediakan oleh Dropbear, sedangkan WinSCP menggunakan SFTP server dari OpenSSH.

- Username: `root`
- Password: `root`

## Penjadwalan Bel

Edit file:

```
/etc/schoolbell/config.yml
```

Contoh format jadwal:

```yaml
schedule:
  - name: "Masuk Pagi"
    time: "07:00"
    days: ["mon", "tue", "wed", "thu", "fri"]
    audio: "/usr/share/schoolbell/bell.wav"
    repeat: 1
    interval_seconds: 2
```

## Output HDMI

Pengaturan HDMI berada di `board/raspberrypi2/schoolbell/config.txt` untuk memaksa audio HDMI aktif.
