# CH592 OTA

1.5.5 / HA0.6.20: before an explicit update or settings connection, discard this meter’s old ESPHome host service table. This avoids wasting an advertising cycle on a normal/OTA mode cache mismatch; retain capability reads and checked cache recovery. The optimization is in HA; firmware changes only its version. Metering, optics, sampling, sleep, battery, normal 300 ms/minute advertising, complete image writes and CRC are unchanged. Matching builds, firmware fault tests and 84 HA regressions pass; physical 1.5.4→1.5.5 OTA passed; measured results and limits follow. Publish OTA images only; full recovery remains local.

Physical 1.5.4→1.5.5 OTA passed: the successful run took 122.8 s, including wake 72.745 s (4 attempts), connection 4.926 s, erase 1.125 s, upload 37.480 s, whole-image CRC 1.330 s, END 0.144 s and reboot confirmation 5.003 s. HA confirmed 1.5.5, 100%, OTA off, preserved 22.52 m³ and resumed normal advertisements. A preceding run timed out after 180.2 s during wake without erasing/programming; the retry succeeded. The shorter successful run does not establish overall reliability or a guaranteed speedup. Power was not measured.

Physical 1.5.3→1.5.4 OTA succeeded in 181.0 s: wake wait 129.163 s (7 attempts), connection 4.330 s, erase 1.209 s, upload 39.716 s, whole-image CRC 1.433 s, END 0.140 s and reboot confirmation 5.004 s. HA confirmed 1.5.4, 100%, OTA off and the preserved 22.51 m³ reading. Normal advertising resumed the following minute; stale connection messages and wake errors cleared on success. Connection retries remain the main delay. Daily power policy is unchanged; current and battery lifetime were not measured.

0.6.18 / firmware 1.5.3: bound actual GATT read I/O by the remaining deadline and reject late replies. Read timeouts/disconnects use link recovery instead of chunk fallback. Firmware requires full legacy VERIFY coverage and verifies the boot flag. The paired IAP checks erase/write results, compares the entire copied image and commits the flag before backup cleanup. Replacing IAP requires the local full wired HEX; regular OTA cannot update it. 79 HA regressions and firmware fault tests pass; physical wired/future OTA testing is pending. Recovery stays local.

0.6.17 / firmware 1.5.2: grant a fresh five-second idle window when an OTA link is established; repeated connected events cannot extend it and the total session limit remains. Re-check OTA entry before smaller-chunk retries; expose wake attempts, elapsed time and last error. Use distinct chip and counter icons while preserving custom names/icons. Retain normal radio timing, metering, battery curves and keys. 74 HA tests and firmware tests pass; physical OTA to 1.5.2 succeeded.

Physical 1.5.1→1.5.2 OTA succeeded in 63.7 s: wake wait 13.111 s, connection 3.560 s, erase 1.028 s, upload 39.350 s, whole-image CRC 1.499 s, END 0.128 s and reboot confirmation 5.007 s. One wake attempt, no connection retries; HA confirmed 1.5.2, 100%, normal mode and 22.51 m³, with distinct chip/counter icons. Entry during this upgrade still ran on 1.5.1; the new 1.5.2 idle timing needs observation on a future update. The shorter total cannot be attributed entirely to that fix.

0.6.16 / firmware 1.5.1: bounded asynchronous whole-image CRC, cache invalidation before mode changes, and acknowledged scheduled reboot. Keep complete FF programming. Fast CRC requires installed firmware 1.5.1; upgrading from 1.5.0 retains byte verification. Physical 1.5.0→1.5.1 OTA and a protocol-7 reinstall both succeeded: whole-image CRC took 1.33 s. The reinstall took 205.9 s overall due to wake/link retries, with about 48.4 s from the successful connection to completion. Weak signal and short windows still affect total time.

0.6.15 / firmware 1.5.0: keep the first click visibly active throughout preparation and the background OTA task, and reject duplicate clicks during download. Revert sparse programming after 0.6.14 failed physical verification at 93%; write and verify the complete image including FF padding. Upgrade the integration before retrying. Firmware 1.5.0 retains the early post-OTA announcement and normal idle advertising schedule; physical OTA from 1.4.9 to 1.5.0 is confirmed by HA (158.3 s including wake waits and retries).

0.6.13: batch verification with full byte comparison and fewer BLE round trips; avoid frontend request timeouts.

0.6.12: fix OTA stuck at 0% after wake by promptly connecting, validating the OTA channel, and invalidating stale GATT caches.

0.6.11: label the paired BTHome default version text entity Firmware, preserving custom names. Firmware 1.4.9.

0.6.10: clicking Write gas/threshold now wakes the device and writes automatically. Editing a draft alone starts no connection or write. Fixes threshold framing, cached GATT tables and cancellation. Firmware 1.4.8 is recommended. Results are reported after a successful write.

0.6.9 with firmware 1.4.7: click Update → download and verify locally → wake OTA through the next normal advertising window → upload, verify and confirm reboot. No idle connection or OTA session is started. Normal advertisements remain about 300 ms per minute but now accept connections; power consumption has not been measured. Installing this firmware from an older release still requires the existing B-button entry or a private wired-flash image. Host tests pass; physical short-window connections and complete OTA remain unverified.

0.6.8: the update flow is now fixed as “click Update → download and verify to HA local storage → wait for OTA → upload and verify → reboot to normal mode”. Manifest polling only checks for a version; it does not download in the background. OTA mode closes after a fresh target-version BTHome broadcast.

0.6.7: use the current raw advertisement so stale merged BTHome fields cannot hide OTA mode; wait for OTA before connecting after an Update click; clear and rediscover a cached phone-settings GATT table. Click Update first, then hold B for at least 12 seconds (20 seconds for the first cache reset).

**Language: [中文（默认）](README.md) | English**

Home Assistant custom integration for updating a **CH592 BLE gas-meter broadcaster** through a Home Assistant Bluetooth proxy (ESPHome Bluetooth Proxy) and the WCH BackupUpgrade protocol.

The device stores the new image in Image B, verifies it, and lets the IAP copy it to Image A after reboot. If a step fails, the old image keeps running. The firmware version is advertised through BTHome text object `0x53`.

- Integration: <https://github.com/ChicLSJ/ch592_ota>
- Firmware and enclosure files: <https://github.com/ChicLSJ/ch592-gas-broadcaster>

> Firmware 1.4.4: release B after about 5 seconds for nRF Connect, or keep holding to about 10 seconds for OTA. Five idle seconds after release returns to normal operation; OTA commands refresh the timer. Prepare the action first. Older firmware up to 1.4.3 uses B for about 3 seconds. Firmware 1.4.4 is built and host-tested; physical validation is pending. Historical time/supply tests below apply to the previous release.

## Tested status

| Item | Value |
|---|---|
| Integration | **0.6.17** |
| Firmware manifest | **1.5.2** |
| Typical update time | 1.4.9 to 1.5.0: **158.3 s** (wake 77.0, connect/erase 4.6, upload 31.3, verify 37.4, reboot 8.1) |
| OTA supply test | CR2032, **3.04 V**, no brownout |

## How it works

Manifest polling only reads release metadata. After you click **Update/Install**, the integration downloads and verifies the image into `.storage/ch592_ota/firmware/`. Firmware 1.4.7+ is then woken remotely through a normal advertising window; older firmware still requires holding B for about 10 seconds. The device enters OTA service `0xFEE0` / characteristic `0xFEE1`. After upload and verification, it reboots to normal BTHome mode and the update closes. A missed advertising window is retried; the wake attempt times out after three minutes. B remains a manual fallback.

PROGRAM and protocol-6 VERIFY use 128-byte chunks; older protocols retain 64-byte VERIFY. Protocol 6 reads cumulative compare status once per 16 chunks. These limits avoid long-write behavior in ESPHome Bluetooth Proxy and match the CH592 flash page implementation.

## Installation

### HACS

1. Open HACS → ⋮ → **Custom repositories**.
2. Add `https://github.com/ChicLSJ/ch592_ota` and select **Integration**.
3. Install **CH592 OTA**, then restart Home Assistant.

### Manual

```bash
cd /config
git clone --depth 1 https://github.com/ChicLSJ/ch592_ota.git /tmp/ch592_ota_repo
cp -rf /tmp/ch592_ota_repo/custom_components/ch592_ota /config/custom_components/
rm -rf /tmp/ch592_ota_repo
```

Then go to **Settings → Devices & services → Add integration** and search for **CH592 OTA**.

The Home Assistant Bluetooth stack must have a connectable ESPHome proxy:

```yaml
esp32_ble_tracker:
  scan_parameters:
    active: true
bluetooth_proxy:
  active: true
```

## Configuration

| Field | Meaning |
|---|---|
| Bluetooth address | The CH592 device address, in uppercase `AA:BB:CC:DD:EE:FF` form |
| Device name | Fallback display name; OTA entities join the BTHome device |
| Firmware path | Optional local `/config` fallback image |
| Manifest URL | Optional override; leaving it empty uses the GitHub manifest |
| Auto install | Start an update when a newly entered OTA device is detected |

The default manifest is:

```text
https://raw.githubusercontent.com/ChicLSJ/ch592-gas-broadcaster/main/firmware/manifest.json
```

The manifest contains `version`, `file`, `size`, `crc32`, and `sha256`. The integration checks all available values before flashing.

## Updating

1. When HA reports a new version, click **Update/Install** on the update entity.
2. Wait for the local download and size/CRC32/SHA-256 verification to finish.
3. With firmware 1.4.7+, HA catches the normal advertising window and wakes OTA automatically. After acknowledgement it promptly connects and validates OTA before uploading. Older firmware requires holding B for **about 10 seconds** for its first upgrade.
4. Wait for the new-version normal BTHome broadcast. That closes OTA mode and completes the update.

If B is held before step 1, no download or upgrade starts; the device returns to normal mode after its five-second idle timeout. You can also call:

```yaml
action: ch592_ota.flash
data:
  firmware: www/firmware/ch592_ota.bin
  version: "1.4.4"
  chunk: 128
```

Keep WCH-Link wired recovery available before the first OTA and do not interrupt power during erase, write, verify, or reboot. If the device is already in OTA mode when Home Assistant starts, let it advertise normally once before relying on automatic detection.

## Gas value and pulse threshold

Recent firmware exposes optional controls for the gas target and the optical pulse threshold. Values are drafts until the corresponding **Write** button is pressed. If the device is not in OTA mode, the integration keeps the pending write briefly and applies it after the next B-button entry.

- `number.*_gas_target` + `button.*_write_gas_value`
- `number.*_pulse_threshold` + `button.*_write_pulse_threshold`
- `button.*_abort_ota` cancels an active update

## Reloading code

After copying a small code change, call `ch592_ota.reload_code` from Developer Tools → Actions. A Home Assistant restart is still required after changing `manifest.json`, adding modules, or after repeated hot reloads.

The integration and firmware are provided for the matching CH592 product hardware. Keep a wired recovery path available and verify the device model before updating.
