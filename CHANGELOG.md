# 0.6.22

1.5.6 / HA0.6.22：移除 0.6.21 的临时唤醒诊断，保留等待新广播的修复。1.5.5→1.5.6 实体 OTA 已成功：全程 126.8 秒，等待唤醒 77.2 秒（4 次尝试），上传和完整 CRC 约 50 秒。固件 1.5.6 仅更新版本号。集成代码不公开，仅发布更新说明。

1.5.6 / HA0.6.22: removed the temporary wake diagnostics from 0.6.21 and kept the wait-for-advertisement fix. Physical 1.5.5→1.5.6 OTA succeeded in 126.8 s, with 77.2 s of wake wait (4 attempts) and about 50 s for upload and whole-image CRC. Firmware 1.5.6 changes only the version. Integration code is not published.

# 0.6.21

蓝牙代理暂未收到设备广播时，等待下一次广播再连接，不再空转；单轮唤醒等待由 180 秒延长到 240 秒。

When the Bluetooth proxy has not yet seen the device, wait for the next advertisement instead of spinning; a single wake round now allows 240 s instead of 180 s.

# 0.6.20

1.5.5 / HA0.6.20：显式点击更新或写值时，在连接前清除本设备在ESPHome代理的旧主机服务表，避免普通模式和OTA模式切换时因缓存失配浪费一轮广播；保留能力读取和异常缓存重试。此优化位于HA，固件仅更新版本号。计量、光照、采样、休眠、电量及约每分钟300毫秒普通广播不变，完整镜像写入和CRC校验不变。双构建、固件故障测试和84项HA回归通过；1.5.4→1.5.5实体OTA已成功：成功轮122.8秒，等待唤醒72.745秒（4次尝试）、连接4.926秒、擦除1.125秒、上传37.480秒、完整CRC1.330秒、END0.144秒、重启确认5.003秒。HA确认1.5.5、100%、OTA关闭，燃气22.52m³保留，普通广播恢复。此前一轮180.2秒唤醒超时，未进入擦写，随后重试成功；不能把成功轮较短耗时等同为整体可靠性或提速保证。未测功耗。仅公开OTA镜像，完整烧录包仅本地。

1.5.5 / HA0.6.20: before an explicit update or settings connection, discard this meter’s old ESPHome host service table. This avoids wasting an advertising cycle on a normal/OTA mode cache mismatch; retain capability reads and checked cache recovery. The optimization is in HA; firmware changes only its version. Metering, optics, sampling, sleep, battery, normal 300 ms/minute advertising, complete image writes and CRC are unchanged. Matching builds, firmware fault tests and 84 HA regressions pass; Physical 1.5.4→1.5.5 OTA passed: the successful run took 122.8 s, including wake 72.745 s (4 attempts), connection 4.926 s, erase 1.125 s, upload 37.480 s, whole-image CRC 1.330 s, END 0.144 s and reboot confirmation 5.003 s. HA confirmed 1.5.5, 100%, OTA off, preserved 22.52 m³ and resumed normal advertisements. A preceding run timed out after 180.2 s during wake without erasing/programming; the retry succeeded. The shorter successful run does not establish overall reliability or a guaranteed speedup. Power was not measured. Publish OTA images only; full recovery remains local.

# 0.6.19

中文：写值、写阈值或OTA成功后清除旧连接提示和上次唤醒错误，保留尝试次数/耗时诊断；失败时保留错误。包含0.6.18实际GATT读取期限修复。配套1.5.4仅更新应用版本，作为已线刷1.5.3后OTA通道验证；计量、光照、电量、采样、休眠和普通广播策略不变。完整包仅本地，公开OTA镜像。79项HA回归通过，1.5.3→1.5.4实体OTA已成功：总181.0秒；等待唤醒129.163秒（7次尝试）、连接4.330秒、擦除1.209秒、上传39.716秒、完整CRC1.433秒、END0.140秒、重启确认5.004秒。HA确认1.5.4、100%、OTA关闭，燃气保留22.51m³；下一分钟普通广播恢复，成功后旧连接提示和唤醒错误已清除。本次仍有连接重试，主要耗时在等待唤醒；未改变日常耗电策略，未测实际电流或电池寿命。

English: clear stale connection messages and wake errors after successful settings writes or OTA, while retaining attempt counts and timing; keep errors on failure. Includes 0.6.18 real GATT I/O deadlines. Firmware 1.5.4 changes only the application version to validate OTA from the wired 1.5.3 baseline. Metering, optical processing, battery, sampling, sleep and normal radio policies are unchanged. Publish OTA images only; recovery remains local. 79 HA regressions pass; Physical 1.5.3→1.5.4 OTA succeeded in 181.0 s: wake wait 129.163 s (7 attempts), connection 4.330 s, erase 1.209 s, upload 39.716 s, whole-image CRC 1.433 s, END 0.140 s and reboot confirmation 5.004 s. HA confirmed 1.5.4, 100%, OTA off and the preserved 22.51 m³ reading. Normal advertising resumed the following minute; stale connection messages and wake errors cleared on success. Connection retries remain the main delay. Daily power policy is unchanged; current and battery lifetime were not measured.

# 0.6.18

中文：0.6.18 / 固件 1.5.3：蓝牙 GATT 读取按剩余期限强制超时，拒绝超期结果；读取超时或断链走链路恢复，不触发分片降档。固件修复旧 VERIFY 的完整覆盖门槛和启动标志读回。配套 IAP 检查擦写、完整读回比较和标志提交，通过后才清理备份；IAP 修复需要本地完整有线 HEX，普通 OTA 无法替换引导。79 项 HA 回归及固件故障注入通过，实体有线/后续 OTA 待验证。完整包仅本地。

English: 0.6.18 / firmware 1.5.3: bound actual GATT read I/O by the remaining deadline and reject late replies. Read timeouts/disconnects use link recovery instead of chunk fallback. Firmware requires full legacy VERIFY coverage and verifies the boot flag. The paired IAP checks erase/write results, compares the entire copied image and commits the flag before backup cleanup. Replacing IAP requires the local full wired HEX; regular OTA cannot update it. 79 HA regressions and firmware fault tests pass; physical wired/future OTA testing is pending. Recovery stays local.

# 0.6.17

中文：0.6.17 / 固件1.5.2：OTA连接建立后获得新的5秒无通信窗口，避免较慢连接耗尽原入口期限；重复连接状态不续期，总会话期限保留。修复分片降档重试前未重新检查OTA入口；增加唤醒尝试、耗时与错误诊断。固件版本使用芯片图标，计数使用计数器图标，保留自定义名称/图标。普通广播、计量、电量曲线和按键逻辑保留。74项HA回归和固件测试通过，1.5.1→1.5.2实体升级成功，完整CRC1.499秒、总63.7秒、无连接重试；新固件连接计时需以后升级再观察。

English: 0.6.17 / firmware 1.5.2: grant a fresh five-second idle window when an OTA link is established; repeated connected events cannot extend it and the total session limit remains. Re-check OTA entry before smaller-chunk retries; expose wake attempts, elapsed time and last error. Use distinct chip and counter icons while preserving custom names/icons. Retain normal radio timing, metering, battery curves and keys. 74 HA tests and firmware tests pass; physical OTA to 1.5.2 passed: CRC1.499 s, total63.7 s, no connection retries. Observe the new firmware idle timing on future updates.

# 0.6.16

中文：协议7/能力bit4使用0x89异步分段CRC，绑定请求编号、检查完整镜像和最终结果；不恢复旧同步CRC。旧版保留完整逐字节校验，FF区仍完整写入。END前清理OTA服务缓存；固件1.5.1先响应再延迟重启，减少旧缓存和无响应等待。保留单击准备锁和后台进度；72项回归通过，1.5.0→1.5.1及协议7复测成功；新完整CRC实测1.33秒。整体205.9秒受唤醒和连接重试影响，不能等同为总耗时优化。

English: use nonce-bound bounded CRC only with protocol7/bit4, validating the complete image and result. Keep legacy byte verification and full FF programming. Clear OTA caches before END; firmware 1.5.1 acknowledges before scheduled reboot. Retain first-click progress and preparation lock. 72 tests pass; physical upgrade and protocol-7 reinstall succeeded. Whole-image CRC took 1.33 s; total 205.9 s still included wake/link retries.

# 0.6.15

中文：修复第一次点击更新后状态复位，以及下载期间重复点击导致重复准备的问题。下载、校验和后台OTA全过程由真实状态驱动进度。撤回0.6.14跳过FF填充写入的优化（实体两次在93%同一区间返回0x7D），恢复完整镜像写入和完整校验；校验失败仍不激活新固件。固件1.5.0不变；1.4.9→1.5.0实体升级已成功，158.3秒，HA确认新版本、100%和退出OTA。

English: preserve visible progress from the first click through download and background OTA; suppress duplicate preparation. Revert skipped FF programming after two physical attempts failed verification at 93% in the same range (0x7D). Program and verify the entire image; never activate a failed image. Firmware 1.5.0 is unchanged; physical OTA from 1.4.9 succeeded in 158.3 s, confirmed by HA with the new version, 100% and normal mode.

# 0.6.14

中文：配合固件1.5.0。擦除成功后跳过全FF空白块编程，仍校验整个镜像和启动标记；保留128字节代理兼容上限与批量累计校验。降低电压诊断查询频率；重连成功后清除旧错误提示。1.4.8→1.4.9已完成实体OTA并确认版本与读数。

English: pair with firmware 1.5.0. Skip programming erased FF chunks while still verifying the complete image and boot marker. Keep the proxy-compatible 128-byte limit and batched cumulative verification. Reduce voltage diagnostics queries and clear stale retry errors on reconnect. Physical OTA 1.4.8 to 1.4.9 was confirmed with a fresh version broadcast and preserved meter reading.

# 0.6.13

中文：协议 6 按 MTU 使用最高 128 字节校验分片，每 16 片读取累计错误结果；最后一片使用确认写入作为顺序屏障。保留所有字节校验，未知协议仍逐片确认。安装请求在任务接受后返回，避免前端请求超时报错；重复点击不重复开启任务，连接超时后重新唤醒再重试；清单读取失败不误用旧本地包。

English: protocol 6 verifies with MTU-sized chunks up to 128 bytes and reads cumulative error status every 16 chunks, using an acknowledged final write as an ordering barrier. Every byte is compared; unknown protocols retain per-command checks. Return after accepting the update task to avoid frontend timeouts; repeated clicks do not start another job. Re-enter OTA after a missed connection window and reject old-image fallback after a manifest fetch failure.

# 0.6.12

中文：修复唤醒已确认却一直停在 0% 的问题。确认唤醒后立即连接并校验 OTA 通道，不再等待可能被蓝牙代理缓存抑制的广播；切换模式前清理 GATT 缓存，读取能力核验唤醒句柄。设备整包 CRC 命令在实测中导致断链，改为分段逐字节校验，校验失败不发送激活命令。保留点击后才连接和原广播节奏。

English: fix updates stuck at 0% after an acknowledged wake. Connect and validate OTA promptly instead of waiting for an advertisement suppressed by proxy caching; invalidate GATT caches across mode changes and verify wake capabilities. Use bounded byte comparisons because the synchronous firmware CRC command drops the BLE link; a failed comparison never activates the image. Connections remain explicit-click only.

# 0.6.11

中文：将对应 CH592 的 BTHome 默认“文本”版本实体命名为“固件”（英文系统为 Firmware），保留用户自定义名称；新实体创建后也会处理。配套 1.4.9 实测 OTA。

English: label the paired CH592 BTHome version text entity Firmware, preserving custom names and handling newly created entities. Pair with firmware 1.4.9 for OTA validation.

# 0.6.10

中文：点击写入燃气值或阈值后自动唤醒固件 1.4.7+，编辑草稿不连接设备；写入和升级互斥，取消或失败会清除待写任务。修正阈值帧并重新发现旧 GATT 缓存。配套固件 1.4.8。

English: explicitly clicking Write wakes firmware 1.4.7+; draft edits start no connection. Writes and upgrades are mutually exclusive; cancelled or failed writes are cleared. Fix threshold framing and stale GATT discovery. Pair with firmware 1.4.8.

# 0.6.9

中文：下载并校验固件后才连接原普通广播窗口，自动开启 OTA；旧版保留 B 键首次升级入口。

English: wake OTA through the normal advertisement window only after downloading and verifying the image; retain B entry for older firmware.

# 0.6.8

中文：固定更新顺序为点击更新后下载并校验到 HA 本地，再等待设备 OTA、上传、验证和重启；清单轮询不再后台下载。收到新版本普通广播后关闭 OTA 状态并完成更新。

English: make the update order explicit: click Update, download and verify into HA local storage, wait for OTA, upload, verify, and reboot. Manifest polling no longer downloads in the background. A fresh target-version normal broadcast closes OTA and completes the update.

# 0.6.7

中文：用原始广播识别 OTA，防止旧 BTHome 数据掩盖模式切换；更新先等待 OTA 广播，不抢连手机写值服务；清理旧 GATT 服务缓存后重新发现。保留单 B 分时和松开后 5 秒无通信退出。

English: identify OTA from the current raw packet, wait for OTA before connecting, and clear stale phone-settings GATT caches. Single-button timing and the five-second idle exit are retained.

# 0.6.6

中文：固件实体中英翻译、设备版本同步、提前下载校验，以及重启后新版本广播确认。

English: localize firmware entities, sync the device version, prefetch and verify the image, and confirm the target-version broadcast after reboot.

# 0.6.5

中文：更新 1.4.4 固件的 B 键 5 秒写值、10 秒 OTA 和空闲 5 秒退出说明；保留旧 OTA 协议兼容。

English: update firmware 1.4.4 instructions (B ~5s phone settings, ~10s OTA, 5s idle exit); OTA protocol compatibility retained.

# Changelog

## 0.6.4

- 移除 0.6.3 的 `Gas total (guarded)` 实体、`Reset gas guard` 按钮和
  `ch592_ota.reset_gas_guard` 服务
- 原因：统计归属消费侧，不应由 OTA 集成提供；README 给出等价的模板传感器
  示例（只增不减，回退持续 10 分钟才接受），Derivative / utility_meter 指向它
- 集成保持 OTA、写燃气值、写阈值三项职责

## 0.6.3

- （已由 0.6.4 移出集成）新增 `sensor.*_gas_total_guarded`：只增不减的燃气累计值
  - HA 重启时会重放扫描器保存的旧广播，固件 ≤ 1.4.1 掉电也可能回滚到旧
    DataFlash 记录；原始 `0x4C` 值向后跳会让 Derivative 出现负速率、
    utility_meter 把回跳后的回升记成消耗
  - 新实体只接受不小于当前值的读数（100 000 m³ 满量程回绕除外），向后跳时
    保持旧值，并在属性里暴露 `raw_value_m3` / `blocked_value_m3` /
    `blocked_since`
  - 真实向下校正通过 `button.*_reset_gas_guard`、
    `ch592_ota.reset_gas_guard` 服务（可带 `value`）或一次燃气写入来放行；
    写入成功后基线自动跟随新值
  - 用 `RestoreSensor` 跨 HA 重启保存基线
- 状态属性、实体名与现有实体保持英文风格；设备页新增
  「Gas total (guarded)」与「Reset gas guard」

## 0.6.2

- 新增集成图标与标志：`brand/icon.png`、`logo.png`（含 @2x），
  HA 设备页 / HACS / 集成列表会显示燃气表表盘 + 广播符号的图标

## 0.6.1

- 设备页实体重新分组，数值和写入按钮放在同一组：
  - `Gas target`、`Pulse threshold`、`Write gas value`、`Write pulse threshold`
    全部放进「配置」，不再一半在「控制」、一半在「配置」
  - `Abort OTA` 回到「控制」，配置区只放与数值相关的实体
  - `Cancel pending writes` 保持「配置」，且只在有待写入时出现

## 0.6.0

配合固件 1.4.1，采样阈值可以远程调整（默认 100，可设 20~2000）：

- 新增 `number.*_pulse_threshold`（草稿）、`button.*_write_pulse_threshold`
- 新增服务 `ch592_ota.set_threshold` / `ch592_ota.cancel_threshold`
- 设备端新增 `0x87` 命令，阈值存 DataFlash 块 3；`INFO` byte13–14 上报当前阈值，
  能力位 bit3、协议版本 6。`sensor.*_ota_status` 增加 `device_threshold` /
  `threshold_pending` / `threshold_result`
- 待写入优先级扩展：阈值与燃气值可以同时排入队列，按 B 后**先写阈值、再写燃气**
  （阈值不复位，燃气写入才复位），两者都不会触发自动升级
- 原「取消待写入」按钮改为 `Cancel pending writes`，一次清空两种待写入
  （`unique_id` 未变，现有实体保留）

## 0.5.1

- 固件 < 1.4.0 时调用 `set_gas` 给出明确提示：
  「设备固件不支持写燃气值（需要 1.4.0 及以上），请先升级固件」（原来的
  `设备返回错误状态 0xFE` 太隐晦）

## 0.5.0

配合固件 1.4.0，可以在 HA 里直接写燃气值，不用再长按 +/-：

- 新增 `number.*_gas_target`（草稿，**不会自己写设备**）、
  `button.*_write_gas_value`、`button.*_cancel_pending_gas_write`
- 新增服务 `ch592_ota.set_gas` / `ch592_ota.cancel_gas`
- **待写入优先级**：设备不在 OTA 模式时点写入 → 记为待写入（15 分钟）；
  长按 B 后集成**先写燃气值、跳过自动升级**。升级进行中点写入会被拒绝
- `sensor.*_ota_status` 增加 `gas_pending` / `gas_result` 属性；
  `number` 实体带 `device_value_m3`（设备当前读数）
- 顺带解析 BTHome `0x4C` 燃气对象，草稿默认显示设备当前值

设备要求：固件 ≥ 1.4.0（`INFO` 能力位 bit2）。老固件调用会报「设备返回错误状态」。

## 0.4.9

- 本地固件文件缺失时不再打 warning（云端清单已成为主力，本地镜像只是兜底）。
  只有配置里**显式填了固件路径**时才提示，否则走 debug。

## 0.4.8

- 新增开发用热重载服务 `ch592_ota.reload_code`，改动后不用重启 HA；改版本号或新增实体平台仍需重启。

## 0.4.7

- **修复升级成功后卡在 98 % 报失败**：普通 BTHome 广播的 `service_uuids` 里也会带
  `0xFFE0/0xFEE0`（代理在之前 OTA 连接时做 GATT 发现后缓存下来的），于是每条普通
  广播都被当成 OTA 广播：`firmware_version` 不再更新、`ota_mode` 也不再清零。
  结果固件明明已经是 1.3.1，集成还认为设备是 1.3.0，等满 180 秒报「未看到目标版本」。
- 现在用 **BTHome 的 0xFCD2 服务数据**做判据：OTA 固件从来不发它。
  - 有 fee0 且**没有** fcd2 → OTA 广播
  - 有 fcd2 → 普通广播（更新版本、清除 OTA 模式）

## 0.4.6

- 修复 0.4.4 引入的异常处理错误，上传失败时能看到真实原因
- **HA 重启后不再自动升级遗留的 OTA 模式**：本次启动必须先看到过普通 BTHome 广播，
  才会认为 OTA 广播是「刚按了 B」；否则只在 `auto_note` 里说明原因
- **连接失败不再整体重传**：只有已经传出去数据（进度 > 10%）之后的断链才重传 3 轮，
  连不上就立刻报错并提示「请重新长按 B 键」，不再卡在 1% 好几分钟

## 0.4.5

- **升级过程中持续采样电压**：每传 16 KB 重新读一次设备 `INFO`（约 14 次），
  `vdd_mv` 属性在上传期间会跟着刷新，不再只在连接时采一次
- 新增 `vdd_min_mv`：本次上传过程中见到的最低电压，升级结束后保留，
  用来判断电池余量（新电池满电静态 ~3.0 V，负载下允许短暂下探）
- 采样失败只记 debug，绝不影响上传

## 0.4.4

- **链路中断后自动整体重传**：上传过程中断链（不是命令报错）时会重新连接、
  重新擦写上传，最多 3 轮。设备掉线后仍会在 OTA 模式停留 8 分钟，而一次
  128 字节上传只要 ~35 秒，重传比放弃划算得多
- CRC32 校验前停 0.5 秒：设备计算 216 KiB 校验期间会阻塞蓝牙任务，
  先让链路安静一下再发命令

## 0.4.3

- `sensor.*_ota_status` 增加三个实测属性：`chunk`（本次实际分片）、
  `vdd_mv`（设备在 OTA 模式测到的电压）、`duration_s`（本次升级总耗时），
  另加 `mtu`、`verify_chunk`、`device_protocol`
- 这些属性在每次升级开始时重置，升级结束后保留，方便对照记录

## 0.4.2

- PROGRAM 分片上限 240 → **128**。ESPHome 代理对超过 128 字节的写入会退化成
  prepare/execute 长写（每片要十几次往返，慢且中途容易断），实测 240 字节跑到
  12% 就失败、然后整个上传从 1% 重新来一遍。128 字节是单包写入，也不再跨
  256 字节页。

## 0.4.1

- CRC32 校验不通过时自动退回逐字节校验（会报出第一个不一致的偏移）。
  这样即使设备端 CRC 命令有问题也不会变成死路，只多花几分钟。

## 0.4.0

配合固件 1.3.0，把升级时间压到 1~2 分钟：

- **校验改成一次往返**：设备新增 `0x85` 命令，自己算 Image B 的 CRC32（与
  `zlib.crc32` 一致）；客户端比对一次即可，省掉整镜像重传的逐字节校验
  （原来约占总时间 40%）。旧固件不支持时自动退回逐字节校验
- **OTA 模式电压上报**：设备在 `INFO` 响应里带上 PA9 实测电压，
  `sensor.*_ota_status` 的 `vdd_mv` 属性显示升级过程中的真实电压
- 能力位 bit1 = CRC32 校验，协议版本 4

## 0.3.7

- 修复升级完成后进度卡在 98 % 两三分钟：只要设备已经广播出目标版本就直接判成功，
  不再额外等一条新的广播（开机那条广播常常在记录基准计数之前就到了，
  于是要多等到下一次 60 秒广播才收尾）

## 0.3.6

- **修复校验阶段卡死**：VERIFY 分片从 240 退回 64。`FLASH_ROM_VERIFY` 和
  `FLASH_ROM_WRITE` 用同一套 256 字节页机制，240 字节校验写入会卡住
  （实测 1 分钟只前进 1%），PROGRAM 的 240 字节分片不受影响
- 校验失败时报出具体偏移，例如 `校验失败 @0x03A40: 设备返回错误状态 0x01`
- 连接失败时的错误信息补上处理建议：「设备已退出 OTA 模式，请重新长按 B 键 3 秒后重试」

## 0.3.5

- **修复长按 B 不自动升级**：OTA 广播改由 0xFEE0 判定，且**先于** BTHome 解析，
  不再被同一地址的 BTHome 广播覆盖回普通模式
- 不再用设备名判断 OTA 模式：HA 会把这个地址的设备名缓存成 `GasMeter OTA`，
  普通广播也会带这个名字
- `binary_sensor.*_ota_mode` 新增 `auto_note` 属性，直接显示自动升级没启动的
  原因（选项关闭 / 已有任务 / 没有清单 / 没有新固件）或「开始自动升级到 x.y.z」

## 0.3.4

- 配合固件 1.2.9：设备在 `INFO` 响应里上报能力位，支持后 PROGRAM 分片从
  64 提升到 240 字节（按 256 字节 Flash 页拆分由设备侧完成）
- 旧固件（无能力位）继续用 64 字节，不受影响
- 安装失败时的分片回退阶梯仍为 `240/192/128/64/32/16`

## 0.3.3

- **上传大幅提速**（一次 20 分钟 → 预计 4~6 分钟，功耗同步下降）：
  - PROGRAM 阶段改用无响应写入（`write without response`），每 32 片才读一次状态，
    不再每片做一次「写 + 读」往返；代理不支持时自动退回带响应写入
  - VERIFY 阶段分片从 64 字节提到 MTU 允许的 240 字节（校验只比较 RAM 与 Flash，
    不受 256 字节页限制），往返次数减少约 4 倍
  - 状态读取失败时自动重试两次并退避，不再一次读超时就终止整个上传
- `ota_status` 的 `phase` 属性显示实际 `chunk` / `verify` 分片大小

## 0.3.2

- OTA 广播名匹配改为“包含 ota”（不区分大小写），不再要求与
  `GasMeter OTA` 完全一致
- 自动升级失败且上传进度 < 5% 时自动重试一次（代理首次连接失败很常见）；
  已经传上去一部分的失败不重试，避免重复上传

## 0.3.1

- OTA 模式识别更稳：除了 0xFEE0 服务 UUID，还匹配广播名 `GasMeter OTA`
  和 service data 里的 fee0
- `binary_sensor.*_ota_mode` 增加诊断属性：`ads_total`、`last_name`、
  `last_service_uuids`、`last_service_data_uuids`
- 修复某些代理不把 OTA 广播的 UUID 列在上报里的情况下自动升级不触发的问题

## 0.3.0

- **长按 B 即自动升级**：设备进入 OTA 模式（广播 `0xFEE0`）时，若固件仓库有
  更新版本，集成自动下载并开始 OTA，不需要再在 HA 点“安装”
- 新增选项 `auto_install_on_ota_mode`（默认开启），可关闭恢复手动模式

## 0.2.2

- 修复 HA 2026.11 下集成无法加载的问题

## 0.2.1

- 新增 `button.*_check_for_updates`：立即拉取固件清单，不用等 30 分钟定时
- 检查失败时按钮会报错并带上原因（例如清单 URL 403）

## 0.2.0

- 新增固件清单轮询（默认 30 分钟）：从 Gitee/GitHub 的固件仓库自动检查新版本
- 有新固件时 `update.*` 实体自动提示；安装时直接下载镜像并校验
  size / CRC32 / SHA-256，无需本地固件文件
- 选项里可配置 `manifest_url`，留空关闭自动检查；拉取失败回退本地固件
- `update.*` 的 `extra_state_attributes` 增加 upstream_version、manifest_error 等
- 固件工程与镜像发布到 https://gitee.com/zigbridge/ch592-gas-broadcaster

## 0.1.2

- 新增 HA 原生固件更新实体 `update.*`：设置 → 更新 / 设备页直接安装，带进度
- OTA 实体通过蓝牙连接并入 BTHome 设备页，燃气/电量/信号/OTA 状态集中在一页
- 新增 `binary_sensor.*_ota_mode`（是否已进入 OTA 模式）
- 新增 `button.*_abort_ota`，取消升级不再需要调用服务
- 修改固件路径后自动重载，更新实体重新读取 `.bin.json`
- 修复 BTHome 广播与 OTA 广播同时出现时 `ota_mode` 被误置回的问题

## 0.1.1

- 默认分片 240 → 64 字节，失败自动降 64 / 32 / 16（修复 10% 处的链路超时）
- `flash` 服务新增 `chunk` 字段（16 的倍数，16~64）
- 单次 OTA 超时 600 s → 1800 s
- `ota_status` 的 `phase` 属性显示实际 MTU / 分片，便于排查
- 读取响应失败包装为可重试错误

## 0.1.0

- 首个版本：通过 HA 蓝牙代理直连 CH592，完成 WCH BackupUpgrade OTA
- BTHome `0x53` 固件版本显示、升级后版本核对
- `ch592_ota.flash` / `ch592_ota.abort` 服务
- 固件首字 JAL 校验与 CRC32 校验
