# CH592 OTA

1.5.5 / HA0.6.20：显式点击更新或写值时，在连接前清除本设备在ESPHome代理的旧主机服务表，避免普通模式和OTA模式切换时因缓存失配浪费一轮广播；保留能力读取和异常缓存重试。此优化位于HA，固件仅更新版本号。计量、光照、采样、休眠、电量及约每分钟300毫秒普通广播不变，完整镜像写入和CRC校验不变。双构建、固件故障测试和84项HA回归通过；1.5.4→1.5.5实体OTA已通过，实测与限制见下。仅公开OTA镜像，完整烧录包仅本地。

1.5.4→1.5.5实体OTA已成功：成功轮122.8秒，等待唤醒72.745秒（4次尝试）、连接4.926秒、擦除1.125秒、上传37.480秒、完整CRC1.330秒、END0.144秒、重启确认5.003秒。HA确认1.5.5、100%、OTA关闭，燃气22.52m³保留，普通广播恢复。此前一轮180.2秒唤醒超时，未进入擦写，随后重试成功；不能把成功轮较短耗时等同为整体可靠性或提速保证。未测功耗。

1.5.3→1.5.4实体OTA已成功：总181.0秒；等待唤醒129.163秒（7次尝试）、连接4.330秒、擦除1.209秒、上传39.716秒、完整CRC1.433秒、END0.140秒、重启确认5.004秒。HA确认1.5.4、100%、OTA关闭，燃气保留22.51m³；下一分钟普通广播恢复，成功后旧连接提示和唤醒错误已清除。本次仍有连接重试，主要耗时在等待唤醒；未改变日常耗电策略，未测实际电流或电池寿命。

0.6.18 / 固件 1.5.3：蓝牙 GATT 读取按剩余期限强制超时，拒绝超期结果；读取超时或断链走链路恢复，不触发分片降档。固件修复旧 VERIFY 的完整覆盖门槛和启动标志读回。配套 IAP 检查擦写、完整读回比较和标志提交，通过后才清理备份；IAP 修复需要本地完整有线 HEX，普通 OTA 无法替换引导。79 项 HA 回归及固件故障注入通过，实体有线/后续 OTA 待验证。完整包仅本地。

0.6.17 / 固件1.5.2：OTA连接建立后获得新的5秒无通信窗口，避免较慢连接耗尽原入口期限；重复连接状态不续期，总会话期限保留。修复分片降档重试前未重新检查OTA入口；增加唤醒尝试、耗时与错误诊断。固件版本使用芯片图标，计数使用计数器图标，保留自定义名称/图标。普通广播、计量、电量曲线和按键逻辑保留。74项HA回归和固件测试通过，1.5.1→1.5.2实体升级已成功。

1.5.1→1.5.2实体OTA已成功：总63.7秒，等待唤醒13.111秒、连接3.560秒、擦除1.028秒、上传39.350秒、完整CRC1.499秒、END0.128秒、重启确认5.007秒。本次一次唤醒、无连接重试；HA确认1.5.2、100%、退出OTA，燃气22.51m³，固件/计数图标分别为芯片/计数器。本次连接入口仍由升级前1.5.1控制，1.5.2新计时逻辑需后续升级观测；不能把这次较短总耗时全部归因于该修复。

0.6.16 / 固件1.5.1：支持分段异步完整镜像CRC、模式切换前清理缓存、设备响应后再重启；保留完整FF写入。快速校验要求设备已安装1.5.1；从1.5.0升级本次仍使用完整逐字节校验。1.5.0→1.5.1及同版本协议7复测均成功；完整校验实测1.33秒。复测总205.9秒，含唤醒与连接重试；一次成功连接后的全程约48.4秒，弱信号和短窗口仍影响总耗时。

0.6.15 / 固件1.5.0：修复首次点击后更新状态丢失、下载期间重复点击的问题。撤回0.6.14跳过空白区写入的优化，恢复包含FF填充的完整写入及完整校验；0.6.14在实体设备93%处校验失败，请先升级集成。固件1.5.0保留OTA后提前回报版本和原待机广播节奏，1.4.9→1.5.0已完成实体升级，HA确认版本和成功状态，总158.3秒（含等待广播与重试）。

0.6.13：批量校验减少蓝牙往返，保留完整逐字节检查；修复前端等待升级时超时报错。

0.6.12：修复唤醒后等待广播导致 OTA 卡在 0%，立即连接并核验通道，清理模式切换的 GATT 缓存。

0.6.11：自动将对应 BTHome 默认“文本”版本实体显示为“固件”，保留自定义名称。配套固件 1.4.9。

0.6.10：点击“写入燃气值/阈值”后自动唤醒并写入，不再要求手动按 B；仅编辑输入框不触发连接或写入。修复阈值命令长度、写值通道缓存和取消任务处理。推荐固件 1.4.8，写入成功后显示结果并退出。

0.6.9（配合固件 1.4.7）：点击更新 → 下载并校验到 HA 本地 → 等待普通广播窗口自动唤醒 OTA → 上传、校验、重启确认。平时不建立连接、不打开 OTA；普通广播仍每分钟约 300ms，但改为允许连接，接收开销和实际续航尚未实测。首次从旧固件升级仍需原 B 键入口或本地有线烧录。

0.6.8：更新流程固定为“点击更新 → 下载并校验到 HA 本地 → 启用 OTA 等待设备 → 上传并验证 → 设备重启回普通模式”。清单轮询只检查版本，不会后台下载；升级完成后必须收到新版本普通广播，OTA 模式自动关闭。

0.6.7：读取当前原始广播，避免 HA 合并旧 BTHome 数据后漏判 OTA；点击更新后先等待 OTA 广播，避免连接手机写值服务；发现旧 GATT 表时清缓存并重新连接。请先点击更新，再持续按 B 至少 12 秒；首次清理缓存时可按住 20 秒。

**语言：中文（默认） | [English](README.en.md)**

Home Assistant 自定义集成：通过 Home Assistant 的蓝牙代理（ESPHome Bluetooth
Proxy）在线升级 **CH592 BLE 燃气表广播器**（WCH BackupUpgrade / OTA）。


> **固件 1.4.4 的 B 键**：约 5 秒松开为 nRF Connect 手机写值，持续约 10 秒为 OTA。松开后 5 秒没有写值/OTA 通信会返回正常计量；OTA 命令刷新空闲计时。请提前准备好手机或 HA 操作。旧 OTA 1.4.3 及以前仍用 B 约 3 秒。1.4.4 已完成编译和主机逻辑检查，尚待实机验证；下方历史耗时/供电实测不代表本版已完成实机测试。

设备端用 WCH 备份升级方案：OTA 镜像写入 Image B，校验通过后 IAP 在重启时拷贝到
Image A；任何一步失败都会继续跑旧固件。版本号通过 BTHome v2 文本对象 `0x53`
广播，升级完成后 HA 里能直接看到新版本。

- 集成仓库：https://github.com/ChicLSJ/ch592_ota
- 固件仓库：https://github.com/ChicLSJ/ch592-gas-broadcaster

## 当前版本与历史实测

| 项目 | 值 |
|------|-----|
| 集成版本 | **0.6.17** |
| 固件版本 | **1.5.2** |
| 历史版本升级耗时 | 1.4.9→1.5.0实测 **158.3秒**：等待77秒、连接/擦除4.6秒、上传31.3秒、校验37.4秒、重启确认8.1秒 |
| 供电实测 | CR2032 新电池，OTA 负载下 **3.04 V**，全程无下探 |
| 结论 | **CR2032 可以完成 OTA**；之前跑不下来是耗时太长（约 20 分钟） |

设备：MAC `0C:3D:5E:54:BC:6F`，HA 里是 BTHome 设备 “BTHome sensor BC6F”。

## 它是怎么工作的

**设备端**（`peripheral.c` 的 OTA 分支）

- 1.4.7 起由 HA 在更新文件校验后自动请求进入 OTA；旧版或手动备用入口为长按 B 约 10 秒。随后复位并启动 OTA 外设，
  广播服务 `0xFEE0`（特征 `0xFEE1`），不再发 BTHome 广播
- 命令：`0x80` PROGRAM、`0x81` ERASE、`0x82` VERIFY、`0x83` END、`0x84` INFO、
  `0x85` CRC32（1.3.0 起）、`0x86` 写燃气值（1.4.0 起）、`0x87` 写采样阈值（1.4.1 起）
- `END` 后切换 ImageFlag 并复位，IAP 把 Image B 拷到 Image A

**集成端**

- 用 `write without response` 流式写 PROGRAM，每 32 片读一次状态
  （以前是每片都「写 + 读」，这是原来 20 分钟的主要来源）
- 协议7且支持bit4时使用 `0x89` 分段异步CRC，绑定请求编号并检查完整镜像；旧版使用完整逐字节VERIFY。禁用旧同步 `0x85`，校验失败不激活固件
- 清单轮询只读取版本和校验信息，不下载固件；点击 HA 的“更新/安装”后才下载并校验到本地缓存
- 下载校验成功后才进入等待 OTA 阶段；设备出现 `0xFEE0` 广播才连接并上传，避免 OTA 窗口被下载耗尽
- `END` 后等待新的普通 BTHome 版本广播；收到后 OTA 模式关闭，更新实体恢复为最新状态

## 分片规则（重要，不要随意改）

| 阶段 | 分片 | 原因 |
|------|------|------|
| PROGRAM | **128**（上限 `OTA_CHUNK_MAX`） | ESPHome 代理对超过 128 字节的写会退化成 prepare/execute 长写，每片十几次往返，既慢又容易断链（240 字节实测跑到 12% 就失败） |
| VERIFY | **128**（协议6，16片一组；旧协议64） | 每组末片确认后读取累计错误；比较整个镜像，避免代理长写与逐片往返。 |
| 设备能力 | `INFO` byte9 | bit0 = PROGRAM 按 256 字节页拆分（固件 ≥ 1.2.9）；bit4 = 支持 `0x89` 分段CRC（协议7，固件≥1.5.1）；旧bit1同步CRC不启用。老固件不上报能力位时自动按 64 字节传 |
| 失败回退 | 128 → 64 → 32 → 16 | 每降一档都会重新擦写整片，代价高，所以默认值要选对 |

## 安装

### 方式一：HACS / 市场（推荐）

HACS 只识别 GitHub 仓库：

1. HACS → 右上角 ⋮ → **自定义仓库**；
2. 添加 `https://github.com/ChicLSJ/ch592_ota`，类型选 **集成（Integration）**；
3. 搜索 “CH592 OTA” 安装，然后重启 HA。

也可以按方式二或三手动安装。

### 方式二：git clone

```bash
cd /config
rm -rf /tmp/ch592_ota_repo
git clone --depth 1 https://github.com/ChicLSJ/ch592_ota.git /tmp/ch592_ota_repo
cp -rf /tmp/ch592_ota_repo/custom_components/ch592_ota /config/custom_components/
rm -rf /tmp/ch592_ota_repo
```

### 方式三：下载 ZIP

- GitHub：`https://github.com/ChicLSJ/ch592_ota/archive/refs/heads/main.zip`

解压后把 `custom_components/ch592_ota` 复制到 `/config/custom_components/`。

装好之后：**设置 → 设备与服务 → 添加集成 → 搜索 “CH592 OTA”**。

需要 HA 的 `bluetooth` 集成，以及可连接的 ESPHome 代理：

```yaml
esp32_ble_tracker:
  scan_parameters:
    active: true
bluetooth_proxy:
  active: true
```

## 更新集成（不用每次都重启 HA）

复制文件后调用新服务，**1~2 秒**生效：

```
开发者工具 → 动作 → ch592_ota.reload_code
```

仍需真正重启 HA 的情况：

- 改了 `manifest.json`（版本号、依赖）
- 新增实体平台 / 新增文件（模块第一次导入）
- 连续热重载多次后出现重复实体之类的怪现象

建议：攒几次小改动热重载验证，稳定后重启一次收尾。

## 配置

| 字段 | 示例 | 说明 |
|------|------|------|
| 蓝牙地址 | `0C:3D:5E:54:BC:6F` | BTHome 设备的 MAC，大写 |
| 设备名称 | `CH592` | 备用名称；OTA 实体会并入 BTHome 设备页 |
| 固件路径 | `www/firmware/ch592_ota.bin` | 相对 `/config`，必须在 config 目录内 |
固件路径只是**兜底**：清单能拉到就以云端为准，拉不到才用本地 `.bin`。
只用云端升级的话，把路径留空、本地文件删掉即可（0.4.9 起不会再刷 warning）；
要保留离线兜底路径的话，记得每次发布固件时同步覆盖本地文件，否则会变成旧镜像。

### 固件自动检查

集成默认每 30 分钟拉取 GitHub 固件清单：

```
https://raw.githubusercontent.com/ChicLSJ/ch592-gas-broadcaster/main/firmware/manifest.json
```

清单里有 `version`、`size`、`crc32`、`sha256`、`file`、`notes`。发现新版本时
`update.*` 自动变成「有更新」，但只显示更新信息；点击“更新/安装”后才下载镜像，
并校验大小 / CRC32 / SHA-256。校验后的文件保存在 HA 的 `.storage/ch592_ota/firmware/`，
下次重试会复用同一份校验通过的文件。想立刻检查：按 `button.*_check_for_updates`。

## 升级

### 推荐：点击更新（1.4.7 起自动唤醒）

1. HA 出现新版本后，点击更新实体的“更新/安装”；
2. HA 下载并校验固件，完成后进入“等待 OTA”状态；
3. 设备已是 1.4.7 或更新版时，HA 自动等待普通广播窗口连接并开启 OTA；漏过窗口会重试，最多等待约 3 分钟。旧版首次升级仍需长按 B 约 10 秒；
4. 设备确认唤醒后立即连接 OTA 并校验通道，再上传、校验；设备重启并收到新版本普通广播后，更新流程关闭。无需按 B。

如果已是最新版本，进入 OTA 模式不会做任何升级，设备在松开 B 后无 OTA 通信约 5 秒自动退出（1.4.4）。

想改回手动：**设置 → 设备与服务 → CH592 OTA → 配置 → 设备进入 OTA 模式时自动
升级** 取消勾选。

> 如果先长按 B、没有在 HA 点击更新，集成不会下载或升级；设备会在无通信约 5 秒后退出。
> HA 重启后如果设备还停留在此前的 OTA 模式里，集成**不会**自动升级——必须先在
> 本次启动中看到过一条普通 BTHome 广播，才会把 OTA 广播当成「刚按了 B」。

### 手动

在 **设置 → 系统 → 更新**、设备页面或仪表板卡片里点「安装」。

临时指定固件/分片时用服务：

```yaml
action: ch592_ota.flash
data:
  firmware: www/firmware/ch592_ota.bin
  version: "1.4.1"
  chunk: 128      # 16 的倍数，16~240；默认按设备能力自动选
```

取消升级：`button.*_abort_ota` 或 `ch592_ota.abort`。

## 燃气值校正（0.5.0 + 固件 1.4.0）

不用再长按 +/- 刷数值，可以在 HA 里直接把读数写进去。

1. 在 `number.*_gas_target` 里填目标值（单位 m³，0.001 分辨率）——
   **它只是草稿，填了不会写设备**；
2. 点 `button.*_write_gas_value`：
   - 设备已在 OTA 模式 → 立刻写入并复位；
   - 设备不在 OTA 模式 → 记为「待写入」（15 分钟有效），此时长按 B 约 10 秒，
     集成看到 OTA 广播后会**先写燃气值、不升级**；
3. 想放弃待写入：点 `button.*_cancel_pending_gas_write` 或调
   `ch592_ota.cancel_gas`。

服务方式：

```yaml
action: ch592_ota.set_gas
data:
  value: 3050.79     # m³
```

设备端行为（固件 1.4.2 起）：燃气值存在**追加式日志**里——两个 4 KB 块、每块
256 条 16 字节记录，每次保存追加一条，块写满才擦除另一块并切换，平均每 256 次
保存才擦一次 Flash。每条写完都读回校验，通过才回成功，然后约 0.2 秒后复位让
广播器加载新值；写入失败时旧值不受影响，掉电最多丢正在写的那一条。

> 1.4.2 会把记录追加到块中间，降级到 1.3.x / 1.4.x 老固件前请先在集成里重写
> 一次燃气值（老固件只读块首记录）。

> **优先级规则**：有待写入的燃气值时，按 B 只写燃气值、不自动升级；
> `update` 实体仍会显示有新版本，之后再按一次 B 即可升级。
> 升级进行中点写入会被拒绝（避免两个任务抢同一个连接）。

## 采样阈值校正（0.6.0 + 固件 1.4.1）

不同表型、玻璃罩脏污、安装距离都会影响红外采样判据，现在阈值可以远程调整，
不用改固件：

1. `number.*_pulse_threshold` 填目标值（20~2000，默认 100）——**草稿，不写设备**；
2. 点 `button.*_write_pulse_threshold`：
   - 设备已在 OTA 模式 → 立即写入（写 DataFlash，**不复位**）；
   - 不在 OTA 模式 → 记为「待写入」，长按 B 约 10 秒后集成先写阈值、跳过自动升级；
3. 取消：`button.*_cancel_pending_writes` 或 `ch592_ota.cancel_threshold`。

```yaml
action: ch592_ota.set_threshold
data:
  value: 120     # 20~2000
```

设备端把阈值存在 DataFlash **块 3（0x3000）**，写入后读回校验，非法值回 `0xFE`，
校验失败回 `0xFF`，旧值不受影响。阈值写完后设备**不复位**，所以同一次 OTA 会话里
还可以接着写燃气值（集成会先写阈值、再写燃气，后者负责复位）。

调参方向：阈值越低越灵敏，可能把噪声计成脉冲（读数虚增）；越高越保守，可能漏计数。
实测余量 190~460，默认 100 已经留足余量，一般只在换表型或环境变化时微调 80~300。
`sensor.*_ota_status` 的 `device_threshold` 属性显示设备当前生效值。

## 统计防负数（模板传感器，0.6.4 起不再由集成提供）

原始 BTHome `0x4C` 值会**向后跳**，有两个来源：

- HA 重启时，蓝牙管理器会把扫描器保存的历史广播立即重放一次（HA `bluetooth`
  的 `_async_replay_history_for_callback`）；保存的是旧广告时，燃气值会短暂回退；
- 固件 ≤ 1.4.1 忽略 `EEPROM_WRITE` 返回值，掉电后可能从 DataFlash 里较旧的记录启动
  （1.4.2 起已改为追加日志 + 写后校验）。

这属于消费侧的统计问题，不该由 OTA 集成承担，所以放在模板里：一个只增不减的
累计值，回退持续 10 分钟才接受。平时的旧包重放几分钟内就会被真实广播纠正，不会
传下去；真实的持久回退或人工改小读数会在 10 分钟后放行。

把下面加到 `configuration.yaml`（或 packages）：

```yaml
template:
  - triggers:
      - trigger: state
        entity_id: sensor.sheng_huo_yang_tai_bthome_sensor_bc6f_gas
        id: change
      # 燃气不动时原始实体不会产生状态变化，靠定时触发把当前值带进来
      - trigger: time_pattern
        minutes: "/5"
        id: poll
      - trigger: state
        entity_id: sensor.sheng_huo_yang_tai_bthome_sensor_bc6f_gas
        for: "00:10:00"
        id: stable
    sensor:
      - name: Gas total guarded
        unique_id: gas_total_guarded_bc6f
        unit_of_measurement: "m³"
        device_class: gas
        state_class: total_increasing
        icon: mdi:gas-cylinder
        state: >
          {% set cur = states('sensor.sheng_huo_yang_tai_bthome_sensor_bc6f_gas') | float(-1) %}
          {% set prev = this.state | float(0) %}
          {% if cur < 0 %}
            {{ prev }}
          {% elif trigger.id in ('change', 'poll') and cur < prev
                and not (prev > 99990 and cur < 10) %}
            {{ prev }}
          {% else %}
            {{ cur }}
          {% endif %}
```

实体 ID 跟随 `name`：`sensor.gas_total_guarded`。把 Derivative（消耗速率）和
utility_meter（今日/本月）的源改成它即可，历史统计继续累计。

燃气不走时原始实体不会有状态变化，所以额外加了每 5 分钟的 `time_pattern`
触发：新建/重载后几分钟内就能拿到当前值，不会一直停在 `unknown`；定时触发
同样受向后跳保护。

模板传感器用 `this.state` 继承上一个值，HA 重启后会自动恢复，不需要额外 helper。
真实向下校正（换表、人工改小）会在 10 分钟后被接受，届时消耗统计会出现一次负
跳变；如果不想记进消耗，改完后重置对应的 utility_meter。

## 实体与观测属性

| 实体 | 说明 |
|------|------|
| `update.<device>_firmware` | 固件更新（安装 + 进度） |
| `binary_sensor.<device>_ota_mode` | 是否处于 OTA 模式 |
| `sensor.<device>_ota_status` | `idle` / `running` / `rebooting` / `success` / `failed` / `aborted` |
| `sensor.<device>_ota_progress` | 上传进度 0–100 % |
| `sensor.<device>_firmware_version` | 设备通过 BTHome `0x53` 报告的固件版本 |
| `button.<device>_abort_ota` | 取消升级 |
| `button.<device>_check_for_updates` | 立即检查固件清单 |
| `number.<device>_gas_target` | 要写入的燃气值（草稿，不写设备） |
| `button.<device>_write_gas_value` | 写入燃气值 / 记为待写入 |
| `number.<device>_pulse_threshold` | 采样阈值草稿（20~2000，默认 100） |
| `button.<device>_write_pulse_threshold` | 写入阈值 / 记为待写入 |
| `button.<device>_cancel_pending_writes` | 取消所有待写入（燃气值 + 阈值） |

`sensor.<device>_ota_status` 的属性是排查问题的主要入口：

| 属性 | 含义 |
|------|------|
| `phase` | 细分阶段：`connected mtu=… chunk=…` / `erasing` / `uploading` / `verifying` / `waiting_reboot` / `done` |
| `error` | 失败原因 |
| `chunk` / `verify_chunk` / `mtu` | 本次实际使用的分片与 MTU |
| `vdd_mv` / `vdd_min_mv` | 设备在 OTA 模式测到的电压（上传中每 16 KB 采一次），以及整个过程的最低值 |
| `duration_s` | 本次升级总耗时（秒） |
| `device_protocol` | 设备 OTA 协议版本（1.3.x = 4、1.4.0 = 5、1.4.1 = 6） |
| `device_threshold` | 设备当前采样阈值（≥1.4.1，连接时从 `INFO` 读取） |
| `threshold_pending` / `threshold_result` | 待写入的阈值与最近一次结果 |

`binary_sensor.*_ota_mode` 的属性：

| 属性 | 含义 |
|------|------|
| `auto_note` | 自动升级的结论：「开始自动升级到 x.y.z」或没启动的原因 |
| `ads_total` / `last_name` / `last_service_uuids` / `last_service_data_uuids` | 最近一条广播的样子 |

仪表板示例见 [`dashboards/ch592_ota.yaml`](dashboards/ch592_ota.yaml)。

## 注意事项

1. **设备的 OTA 时间窗**：进入 OTA 模式后，**松开 B 后无通信 5 秒**、**总时长 24 分钟**（1.4.4）
   会自动复位退出。失败后重试必须**重新长按 B**。
2. **升级期间没有 BTHome 数据**：OTA 模式下设备只广播 OTA 服务，燃气/电量停在
   最后一次的值，这是正常的。
3. **不要调大分片**：128 是 ESPHome 代理的安全上限；240 会退化成代理长写并在
   中途断链。校验阶段必须保持 64。
4. **电池**：新 CR2032 在 40 秒 OTA 负载下约 3.04 V，可用；旧电池（低于 ~2.9 V
   静置）建议先换。`vdd_min_mv` 是最直接的判断依据（< 2.6 V 基本到极限）。
5. **USB 烧录只擦代码区**：`firmware/Broadcaster_full.hex` 不含 DataFlash
   （`0x70000`），用 WCH-LinkUtility 时不要选 Chip Erase / 全片擦除，否则燃气值丢失。
6. **广播判定不用设备名**：HA 会把该地址的设备名缓存成 `GasMeter OTA`；普通
   BTHome 广播的 `service_uuids` 里也可能带着 `0xFFE0/0xFEE0`（代理做过 GATT
   发现后的缓存）。集成用 **`0xFCD2` BTHome 服务数据**作为判据：
   有 fee0 且没有 fcd2 = OTA 广播。

## 故障排查

| 现象 / 报错 | 含义与处理 |
|-------------|-----------|
| `Failed to connect after 3 attempt(s)` | 设备没进 OTA 模式或已退出。**重新长按 B 约 10 秒**再试 |
| `校验失败 @0xXXXXX: 设备返回错误状态 0x??` | 写入内容与镜像不一致；先看是否误调大了 VERIFY 分片 |
| CRC或VERIFY不匹配 | 停止升级，不发送激活命令；旧固件继续运行，检查供电与链路后重试 |
| 进度到 12% 又回到 1% | 分片写入失败触发了整体重传（0.4.2 起上限 128，正常不会再出现） |
| 卡在 98% 很久 | 等设备重启后的版本广播。0.4.7 起只要版本已对上就立即判成功；再出现请检查 `firmware_version` 是否在更新 |
| `name 'OtaError' is not defined` | 0.4.4 的 bug，升级到 0.4.6+ |
| `固件已上传，但 180s 内未看到目标版本` | 版本号没刷新：确认 `fw` 是否已变成目标版本（0.4.7 已修判定逻辑） |
| 升级中途断电 | `END` 之前：仍跑旧固件；`END` 之后：下次上电 IAP 继续拷贝 |

## 开发与验证流程

**改 HA 侧代码**（`ble_ota.py` / `coordinator.py` 等）

1. 复制 `custom_components/ch592_ota/` 到 `/config/custom_components/`
2. 调用 `ch592_ota.reload_code`
3. 继续验证

**改固件**

```bash
# 1. 改版本号：APP/include/broadcaster.h 的 FW_VERSION_STRING
# 2. 编译（MounRiver Studio 或命令行 make）
python tools/make_ota_images.py
python tools/publish_firmware.py --repo . --notes "改了什么" --push
# 3. 打 tag + release（GitHub Actions 会为缺失的 v* tag 自动建 release）
```

发布后 HA 里按 `button.*_check_for_updates` 即可看到新版本。

## 版本要点

| 版本 | 关键改动 |
|------|---------|
| 0.1.x | 首个可用版本；分片 240 → 64；原生 update 实体 |
| 0.2.x | 固件清单自动检查、立即检查按钮 |
| 0.3.x | 长按 B 自动升级；OTA 广播判定修正；进度卡 98% 修正 |
| 0.4.2 | PROGRAM 分片上限 128（代理长写退化） |
| 0.4.4 | 断链自动整体重传 |
| 0.4.5 | 上传过程中持续采样电压 + `vdd_min_mv` |
| 0.4.7 | 用 `0xFCD2` 判定广播类型，修复升级成功却报失败 |
| 0.4.8 | `reload_code` 热重载服务 |
| 0.4.9 | 未配置固件路径时本地文件缺失不再告警 |
| 0.5.0 | 燃气值校正：number 草稿 + 写入按钮 + 待写入优先级 |
| 0.6.0 | 采样阈值校正（0x87）：number 草稿 + 写入按钮 + 设备阈值显示 |
| 0.6.1 | 设备页实体重新分组：数值与写入按钮统一放进「配置」 |
| 0.6.2 | 集成图标与标志（`brand/`），HA / HACS 显示燃气表盘图标 |
| 0.6.3 | 曾加入 `Gas total (guarded)` 实体（0.6.4 已移除，改由模板传感器承担） |
| 0.6.4 | 移除 guarded 实体与相关服务/按钮，集成回到纯 OTA/写值职责 |

固件侧：1.2.9 引入按页拆分的 PROGRAM；1.3.0 引入 `0x85` CRC32 校验与 OTA 模式
电压上报；1.3.1 为电池实测版本；1.4.0 增加 `0x86` 燃气值写入；1.4.1 增加
`0x87` 采样阈值写入（DataFlash 块 3，默认 100，可设 20~2000）；1.4.2 把燃气值
改为追加式日志并逐条读回校验，掉电最多丢一条记录；1.4.3 修正保存失败后的
重试计时（按 300 ms 采样节拍，约 15 秒重试）。完整记录见
[CHANGELOG.md](CHANGELOG.md)。
