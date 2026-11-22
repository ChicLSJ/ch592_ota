# CH592 OTA

**Language: [中文](README.md) | English**

A Home Assistant integration for the CH592 BLE gas-meter broadcaster. It updates firmware, writes the gas reading and writes the sampling threshold over an ESPHome Bluetooth proxy.

This repository contains release notes only. The integration code and firmware source are not published, and no download or install files are provided. OTA firmware images and the manifest are published in [ChicLSJ/ch592-gas-broadcaster](https://github.com/ChicLSJ/ch592-gas-broadcaster).

## Current versions

| Item | Version |
|------|---------|
| HA integration | 0.6.22 |
| Firmware | 1.5.6 |

Physical OTA from 1.5.5 to 1.5.6 succeeded in 126.8 s, including 77.2 s of wake wait (4 attempts). Upload and whole-image CRC took about 50 s.

## Usage

1. When HA finds new firmware, click Update/Install on the update entity.
2. HA downloads and verifies the image, then wakes OTA during the device's normal advertising window (firmware 1.4.7 and later). No button press is needed.
3. After upload, verification and reboot, HA sees the new version in a normal advertisement and closes the update.

The device is connectable for only about 300 ms per minute, so waking usually takes one to two minutes. First updates from older firmware still need B held for about 10 seconds.

## Release notes

See [CHANGELOG.md](CHANGELOG.md).
