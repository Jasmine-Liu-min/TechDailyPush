# ☀️ Tech Daily - 科技日报推送工具

每天自动抓取 7 个科技信源，生成精美邮件推送到你的邮箱。零依赖，纯 Python 标准库。

## 信源

### 国内
| 信源 | 内容 |
|---|---|
| 📰 **36氪** | 国内科技商业快讯 |
| 🤖 **量子位** | 国内 AI 行业资讯 |

### 海外
| 信源 | 内容 |
|---|---|
| 🔥 **Product Hunt** | 全球每日新产品发布 |
| 🔶 **Hacker News** | 硅谷科技社区热帖 |
| 🚀 **Show HN** | 开发者新产品展示 |
| 🐙 **GitHub 热门** | 近期高星新开源项目 |
| 💬 **Ask HN** | 科技圈热门讨论 |

## 快速开始

### 1. 配置邮箱

复制示例配置并编辑：

```bash
cp config.example.json config.json
```

编辑 `config.json`，填入你的邮箱信息：

```json
{
  "email": {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender": "你的QQ号@qq.com",
    "password": "QQ邮箱授权码（不是QQ密码）",
    "receiver": "接收邮箱@xxx.com"
  },
  "schedule": "08:00",
  "top_n": 10
}
```

> **QQ 邮箱授权码获取：**
> 1. 电脑浏览器打开 https://wx.mail.qq.com 并登录
> 2. 点击左下角 **设置**
> 3. 找到 **账号与安全** 或 **安全设置**
> 4. 找到 **POP3/SMTP 服务** 或 **IMAP/SMTP 服务**，点击 **开启**
> 5. 开启后点击 **生成授权码**
> 6. 按提示用手机发送短信验证
> 7. 验证通过后会显示一个 **16 位授权码**（如 `abcdefghijklmnop`）
> 8. 复制这个授权码，填入 `config.json` 的 `password` 字段
>
> ⚠️ 授权码不是 QQ 密码，是开启 SMTP 服务后专门生成的独立密码，用于第三方程序发送邮件
>
> ⚠️ 授权码只显示一次，请立即复制保存。如果忘记了，可以重新生成一个新的，旧的会自动失效
>
> 如果在网页版找不到，也可以在 **手机 QQ 邮箱 App** 中操作：设置 → 账号与安全 → 安全登录 → 生成授权码

### 2. 预览测试

```bash
python daily.py --preview
```

会在当前目录生成 `preview.html`，浏览器自动打开预览邮件效果。不会发送邮件。

### 3. 手动发送一次

```bash
python daily.py
```

显示 `✅ 发送成功！` 后去邮箱查收。

## 定时自动发送

### 方式一：GitHub Actions（推荐，不用开电脑）

代码推送到 GitHub 后，每天自动在云端运行推送，无需本地开机。

1. 打开仓库 **Settings → Secrets and variables → Actions**
2. 点 **New repository secret**，依次添加：

   | Name | Value |
   |---|---|
   | `SMTP_SERVER` | `smtp.qq.com` |
   | `SMTP_PORT` | `465` |
   | `SENDER` | 你的发件邮箱 |
   | `PASSWORD` | 邮箱授权码 |
   | `RECEIVER` | 接收邮箱 |

3. 完成后去 **Actions** 页面，点 **Tech Daily Push → Run workflow** 手动触发测试
4. 成功后每天北京时间 09:45 自动推送

### 方式二：Windows 定时任务（需要电脑开机）

### 开启定时任务

**右键 `setup_schedule.bat` → 以管理员身份运行**

会创建 Windows 计划任务，每天 08:00 自动运行脚本发送邮件。

- 关机重启不影响，到点自动运行
- 不需要开着任何窗口
- 电脑必须在运行状态（休眠/关机时不会触发，开机后会补发）

### 开启定时任务

**双击方式：** 右键 `scripts/setup_schedule.bat` → 以管理员身份运行

**命令行方式：** 打开 cmd，输入：
```bash
schtasks /create /tn "TechDaily" /tr "python daily.py的完整路径" /sc daily /st 08:00 /f
```

### 查看定时任务状态

**双击方式：** 双击 `scripts/check_schedule.bat`

**命令行方式：** 打开 cmd，输入：
```bash
schtasks /query /tn "TechDaily"
```

### 手动触发一次（不等到明天）

**双击方式：** 双击 `scripts/run_now.bat`

**命令行方式：** 打开 cmd，输入：
```bash
schtasks /run /tn "TechDaily"
```

### 停止/删除定时任务

**双击方式：** 右键 `scripts/stop_schedule.bat` → 以管理员身份运行

**命令行方式：** 打开 cmd，输入：
```bash
schtasks /delete /tn "TechDaily" /f
```

执行后定时任务彻底删除，不会再自动发送。想重新开启，再运行一次 `setup_schedule.bat` 即可。

### 修改发送时间

1. 先删除旧任务：`schtasks /delete /tn "TechDaily" /f`
2. 编辑 `setup_schedule.bat`，把 `08:00` 改成你想要的时间（如 `07:30`）
3. 重新右键以管理员身份运行

## 其他邮箱配置

### 163 邮箱

```json
"smtp_server": "smtp.163.com",
"smtp_port": 465
```

授权码获取：163 邮箱 → 设置 → POP3/SMTP → 开启 → 生成授权码

### Gmail

```json
"smtp_server": "smtp.gmail.com",
"smtp_port": 465
```

需要开启「应用专用密码」：Google 账号 → 安全 → 两步验证 → 应用专用密码

## 项目结构

```
tech-daily/
│
├── daily.py                # 主程序（抓取 + 生成邮件 + 发送）
├── config.json             # 配置文件（邮箱、发送时间）
├── README.md
│
├── scripts/                # 定时任务管理（双击即用）
│   ├── setup_schedule.bat  #   开启定时发送（右键管理员运行）
│   ├── stop_schedule.bat   #   停止定时发送（右键管理员运行）
│   ├── check_schedule.bat  #   查看任务状态（双击）
│   └── run_now.bat         #   立即发送一次（双击）
│
└── output/                 # 输出文件
    └── preview.html        #   邮件预览（--preview 时生成）
```

## 命令汇总

| 命令 | 说明 |
|---|---|
| `python daily.py --preview` | 预览邮件，不发送 |
| `python daily.py` | 立即抓取并发送一次 |
| `python daily.py --daemon` | 前台定时运行（关窗口就停） |
| 运行 `scripts/setup_schedule.bat` | 创建 Windows 定时任务（推荐） |
| `schtasks /query /tn "TechDaily"` | 查看定时任务状态 |
| `schtasks /run /tn "TechDaily"` | 手动触发一次 |
| `schtasks /delete /tn "TechDaily" /f` | 停止并删除定时任务 |

## 技术实现

- **36氪**：解析页面内嵌 `window.initialState` JSON 数据
- **量子位**：正则提取首页文章链接
- **Product Hunt**：Atom Feed 解析
- **Hacker News / Show HN / Ask HN**：Algolia API
- **GitHub**：GitHub Search API（按 stars 排序近 7 天新项目）
- **邮件**：SMTP SSL，HTML 格式邮件

零依赖，纯 Python 标准库（urllib + re + json + smtplib）。

## License

MIT
