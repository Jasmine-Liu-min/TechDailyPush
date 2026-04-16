# ☀️ Tech Daily - 科技日报推送工具

每天自动抓取多个科技信源，生成精美邮件推送到你的邮箱。零依赖，纯 Python 标准库。

## 信源

| 信源 | 内容 |
|---|---|
| 📰 **36氪** | 国内科技商业快讯 |
| 🤖 **量子位** | 国内 AI 行业资讯 |
| 🔥 **Product Hunt** | 全球每日新产品发布 |
| 🔶 **Hacker News** | 硅谷科技社区热帖 |
| 🚀 **Show HN** | 开发者新产品展示 |
| 🐙 **GitHub 热门** | 近期高星新开源项目 |
| 💬 **Ask HN** | 科技圈热门讨论 |

## 快速开始

### 1. 配置邮箱

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
  "schedule": "09:00",
  "top_n": 10
}
```

<details>
<summary>📌 QQ 邮箱授权码获取方法</summary>

1. 电脑浏览器打开 https://wx.mail.qq.com 并登录
2. 点击左下角 **设置**
3. 找到 **账号与安全** 或 **安全设置**
4. 找到 **POP3/SMTP 服务** 或 **IMAP/SMTP 服务**，点击 **开启**
5. 开启后点击 **生成授权码**
6. 按提示用手机发送短信验证
7. 验证通过后会显示一个 **16 位授权码**（如 `abcdefghijklmnop`）
8. 复制这个授权码，填入 `config.json` 的 `password` 字段

> ⚠️ 授权码不是 QQ 密码，是开启 SMTP 服务后专门生成的独立密码
>
> ⚠️ 授权码只显示一次，请立即复制保存。忘记了可以重新生成，旧的会自动失效

手机端：QQ 邮箱 App → 设置 → 账号与安全 → 安全登录 → 生成授权码

</details>

### 2. 预览测试

```bash
python daily.py --preview
```

生成 `preview.html` 并自动打开浏览器预览，不会发送邮件。

### 3. 手动发送一次

```bash
python daily.py
```

显示 `✅ 发送成功！` 后去邮箱查收。

## 定时自动发送

### 方式一：GitHub Actions（推荐，无需开机）

代码推送到 GitHub 后，每天自动在云端运行，无需本地开机。

1. 打开仓库 **Settings → Secrets and variables → Actions**
2. 点 **New repository secret**，依次添加：

   | Name | Value |
   |---|---|
   | `SMTP_SERVER` | `smtp.qq.com` |
   | `SMTP_PORT` | `465` |
   | `SENDER` | 你的发件邮箱 |
   | `PASSWORD` | 邮箱授权码 |
   | `RECEIVER` | 接收邮箱 |

3. 去 **Actions** 页面，点 **Tech Daily Push → Run workflow** 手动触发测试
4. 成功后每天北京时间 **09:00** 左右自动推送

> ⚠️ **关于定时触发延迟：** GitHub Actions 的 cron 调度不是精确的，免费账户通常会有 5~30 分钟甚至更久的延迟，这是正常现象。手动触发（Run workflow）是即时的，可以用来验证工作流是否正常。

### ❓ 常见问题排查

<details>
<summary>点击展开</summary>

**Q: 定时任务一直不触发？**

1. **确认 workflow 在默认分支上：** GitHub Actions 的 schedule 只会在默认分支（通常是 `main`）上触发
2. **仓库活跃度：** 公开仓库如果 60 天内没有任何 commit，GitHub 会自动禁用 scheduled workflows。去 Actions 页面查看是否有黄色提示，点击 "Enable workflow" 重新启用
3. **时区配置：** 本项目使用了 GitHub 2026 年 3 月新增的 `timezone` 字段，可以直接用 `Asia/Shanghai` 指定北京时间，无需手动换算 UTC。如果你的 GitHub 环境尚未支持此功能，可以改用 UTC 时间：`cron: '0 1 * * *'`（UTC 01:00 = 北京时间 09:00）
4. **修改 cron 后不会立即触发：** 需要等到下一个匹配的时间点才会调度

**Q: 定时触发了但发送失败？**

1. **检查 Secrets 配置：** 确认 5 个 secret（SMTP_SERVER、SMTP_PORT、SENDER、PASSWORD、RECEIVER）都已正确添加
2. **不要使用第三方 keepalive action：** 部分第三方 action 可能被仓库权限策略拦截（报 "Repository access blocked"），导致依赖它的后续 job 也无法运行。本项目已移除 keepalive 依赖
3. **查看运行日志：** 去 Actions 页面点击失败的运行记录，查看具体哪个 step 报错

**Q: 授权码过期了？**

QQ 邮箱授权码在重新生成后旧的会自动失效。去 QQ 邮箱重新生成授权码，然后更新仓库 Settings → Secrets 中的 `PASSWORD`。

</details>

### 方式二：Windows 定时任务（需要电脑开机）

右键 `scripts/setup_schedule.bat` → **以管理员身份运行**

即可创建 Windows 计划任务，每天 **09:00** 自动发送邮件。

- 关机重启不影响，到点自动运行
- 不需要开着任何窗口
- 电脑必须在运行状态（休眠/关机时不会触发，开机后会补发）

**查看任务状态：** 双击 `scripts/check_schedule.bat`

**手动触发一次：** 双击 `scripts/run_now.bat`

**停止定时任务：** 右键 `scripts/stop_schedule.bat` → 以管理员身份运行

**修改发送时间：**
1. 运行 `stop_schedule.bat` 删除旧任务
2. 编辑 `setup_schedule.bat` 中的时间
3. 重新以管理员身份运行 `setup_schedule.bat`

## 其他邮箱配置

| 邮箱 | smtp_server | smtp_port | 授权码获取 |
|---|---|---|---|
| **163** | `smtp.163.com` | `465` | 设置 → POP3/SMTP → 开启 → 生成授权码 |
| **Gmail** | `smtp.gmail.com` | `465` | Google 账号 → 安全 → 两步验证 → 应用专用密码 |

## 项目结构

```
TechDailyPush/
├── daily.py                        # 主程序（抓取 + 生成邮件 + 发送）
├── config.example.json             # 配置示例（复制为 config.json 使用）
├── .gitignore                      # Git 忽略规则（排除 config.json 等敏感文件）
├── .github/workflows/daily.yml     # GitHub Actions 定时任务
└── scripts/                        # 仅本地 Windows 定时任务使用
    ├── setup_schedule.bat          # 开启定时发送（右键管理员运行）
    ├── stop_schedule.bat           # 停止定时发送（右键管理员运行）
    ├── check_schedule.bat          # 查看任务状态（双击）
    └── run_now.bat                 # 立即发送一次（双击）
```

## 命令汇总

| 命令 | 说明 |
|---|---|
| `python daily.py --preview` | 预览邮件，不发送 |
| `python daily.py` | 立即抓取并发送一次 |
| `python daily.py --daemon` | 前台定时运行（关窗口就停） |

## 技术实现

- **36氪**：解析页面内嵌 `window.initialState` JSON 数据
- **量子位**：正则提取首页文章链接
- **Product Hunt**：Atom Feed 解析
- **Hacker News / Show HN / Ask HN**：Algolia API
- **GitHub**：GitHub Search API（按 stars 排序近 7 天新项目）
- **邮件**：SMTP SSL，HTML 格式邮件

零依赖，纯 Python 标准库（`urllib` + `re` + `json` + `smtplib`）。

## License

MIT
