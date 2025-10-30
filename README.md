# Arboris-Novel  | 给写小说的人，一个有意思的写作空间

![GitHub stars](https://img.shields.io/github/stars/t59688/arboris-novel?style=social)
![GitHub forks](https://img.shields.io/github/forks/t59688/arboris-novel?style=social)
![GitHub issues](https://img.shields.io/github/issues/t59688/arboris-novel)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)




你盯着屏幕上闪烁的光标，脑子里有个模糊的想法：一个有意思的故事。但当你试图把它写下来时，却发现自己卡在了「主角叫什么名字」「故事发生在哪里」「第三章该写什么」这些问题上。

**Arboris** 就是在这种时候出现的——它不会替你写作（那样多没意思），但它会在你需要的时候，帮你理清思路、记住细节、提供几个「要不试试这个方向」的建议。

**在线体验：** [https://arboris.aozhiai.com](https://arboris.aozhiai.com) 


**有问题想聊？加群(微信满了...)：**  
<p align="center">
  <img width="294" alt="交流群二维码" src="https://github.com/user-attachments/assets/6d4fe420-f8ae-4fe4-883d-235eb576c83b" />
</p>

---

## 截图看看长什么样

<p align="center">
  <img width="1471" alt="主界面" src="https://github.com/user-attachments/assets/a52d0214-bc1b-4792-8a2b-267b09e47379" />
</p>
<p align="center">
  <img width="1375" alt="角色管理" src="https://github.com/user-attachments/assets/0673faad-43df-4479-83ae-cffa870199a3" />
</p>
<p align="center">
  <img width="1392" alt="大纲编辑" src="https://github.com/user-attachments/assets/b7a7af24-1689-4341-aa78-26b0d74bdddd" />
</p>
<p align="center">
  <img width="1255" alt="写作界面" src="https://github.com/user-attachments/assets/c831d746-8c1a-4ce8-aa1c-9b852da15c11" />
</p>

---

## 它能帮你干什么？

### 📖 管住那些跑偏的设定
写到第五十章突然想不起来男二号的眼睛是什么颜色？世界观里的魔法体系到底有几个等级？  
Arboris 帮你把所有角色、地点、派系的设定都记下来，随时翻阅，再也不会前后矛盾。

### 🧵 把乱糟糟的灵感捋成故事线
脑子里有十几个场景片段，但不知道怎么串起来？  
和 AI 聊聊你的想法，它会帮你梳理出一条主线，从开头到结局的大纲自然就出来了。

### ✍️ 有个不会累的写作搭档
今天状态不好，但又不想断更？让 AI 先写个草稿，你再根据自己的风格改改。  
或者反过来——你写了开头，让它接着往下试试，没准能给你意想不到的灵感。

### 🔄 多版本对比，找到最对味的那一版
AI 生成的内容不一定第一次就完美，但你可以让它多试几版，挑出最喜欢的部分，慢慢"训练"它懂你的笔触。

---

## 为什么要做这个？

因为我觉得我们需要的不是一个"自动生成器"，而是一个**能记住你的世界、理解你的角色、陪你一起推进故事的伙伴**。

所以我们做了 Arboris，并且决定**开源**——因为好的工具应该属于所有创作者。

---

## 快速开始（真的很快）

### 方式一：直接用 Docker 跑起来

```bash
# 1. 复制配置文件
cp .env.example .env

# 2. 改几个必填项（用你喜欢的编辑器打开 .env）
#    - SECRET_KEY: 随便敲点字符，越长越安全
#    - OPENAI_API_KEY: 你的大模型 API Key
#    - ADMIN_DEFAULT_PASSWORD: 管理员密码，别用默认的

# 3. 启动（默认用 SQLite，不需要装数据库）
docker compose up -d

# 搞定！浏览器打开 http://localhost:<端口> 就能用了
```

### 方式二：我想用 MySQL

```bash
# 在 .env 里改一下 DB_PROVIDER=mysql
# 然后用这个命令启动（会自动带上 MySQL 容器）
DB_PROVIDER=mysql docker compose --profile mysql up -d
```

### 方式三：我有自己的 MySQL 服务器

```bash
# 在 .env 里填好你的数据库地址、用户名、密码
# 然后正常启动
DB_PROVIDER=mysql docker compose up -d
```

---

## 环境变量速查表

这些是你可能需要改的配置（完整列表在 `.env.example` 里）：

| 配置项 | 必填吗 | 说明 |
|--------|--------|------|
| `SECRET_KEY` | ✅ | JWT 加密密钥，自己随机生成一串，别告诉别人 |
| `OPENAI_API_KEY` | ✅ | 你的 LLM API Key（OpenAI 或兼容的） |
| `OPENAI_API_BASE_URL` | ❌ | API 地址，默认是 OpenAI 官方的 |
| `OPENAI_MODEL_NAME` | ❌ | 模型名称，默认 `gpt-3.5-turbo` |
| `ADMIN_DEFAULT_PASSWORD` | ❌ | 管理员初始密码，**部署后记得改** |
| `ALLOW_USER_REGISTRATION` | ❌ | 要不要开放注册？默认不开（`false`） |
| `SMTP_SERVER` / `SMTP_USERNAME` | 开注册就得填 | 邮件服务配置，用来发验证码 |

> 💡 **数据存哪？**  
> 默认用 SQLite，数据存在 Docker 卷里。想映射到本地？在 `.env` 里设置 `SQLITE_STORAGE_SOURCE=./storage` 就行。

---

## 一些常见问题

### 基础使用

**Q: 我不会 Docker 怎么办？**  
A: 装一下 Docker Desktop（Windows/Mac）或者 Docker Engine（Linux），然后复制粘贴上面的命令就行。真的不难。

**Q: 我的 API Key 会不会泄露？**  
A: 不会。密钥存在服务器的 `.env` 文件里，不会暴露给前端或用户。

**Q: 可以用其它的大模型吗？**  
A: 只要提供 OpenAI 兼容接口，都可以。改一下 `OPENAI_API_BASE_URL` 就行。

**Q: 我改了代码怎么办？**  
A: 欢迎！提 PR 或者 Issue 都行。

### 生成小说时的常见错误

**Q: 提示"未配置默认 LLM API Key"怎么办？**  
A: 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确配置。如果是个人用户，也可以在个人设置中配置自定义 API Key。

**Q: 生成时提示"今日请求次数已达上限"？**  
A: 系统管理员可能设置了每日请求限制。解决方案：
- 等到明天再试
- 在个人设置中配置自己的 API Key（不受系统配额限制）
- 管理员调整配额限制（修改 `daily_request_limit` 配置）

**Q: 提示"AI 服务响应超时"或"无法连接到 AI 服务"？**  
A: 网络或 API 服务问题导致。可以：
- 检查网络连接是否正常
- 确认 `OPENAI_API_BASE_URL` 配置是否正确
- 如果使用自建服务，检查服务是否正常运行
- 稍后重试

**Q: 提示"AI 响应因长度限制被截断"？**  
A: 生成的内容超过了模型的输出限制。建议：
- 使用支持更长输出的模型

**Q: 提示"AI 未返回有效内容"或"AI 服务内部错误"？**  
A: AI 服务端出现问题。通常是暂时性的，可以：
- 大多是LLM服务的问题，尤其是逆向的API。
- 检查 API Key 是否有效且有足够余额
- 查看后端日志获取详细错误信息

**Q: 提示"蓝图中未找到对应章节纲要"？**  
A: 在生成章节内容前，需要先在蓝图（大纲）中创建对应章节的纲要。请先完善章节大纲再进行生成。

**Q: 提示"未配置摘要提示词"？**  
A: 系统缺少必要的 Prompt 配置。管理员需要在后台配置名为 `extraction` 的提示词模板，用于生成章节摘要。

**Q: 提示"AI 返回的内容格式不正确"或 JSON 解析错误？** ⭐ **非常常见**  
A: 这是最常见的问题之一。AI 返回的内容无法被解析为有效的 JSON 格式。原因和解决方案：
- **原因 1：模型能力不足** - 某些模型难以稳定输出结构化 JSON
  - 解决：切换到能力更强的模型
  - 或使用支持 structured output 的模型
- **原因 2：内容过长** - 某些逆向API可能无法支持长输出。

- **临时解决方案：**
  - 多试几次（有时是偶发问题）
  - 更换不同的 AI 模型

**Q: 生成的内容质量不理想怎么办？**  
A: 可以尝试：
- 完善角色、地点、派系等设定信息
- 优化章节纲要，提供更详细的指引
- 使用多版本生成功能，让 AI 生成多个版本后挑选最佳的
- 调整使用的模型，需要长上下文的

---

## 技术栈（给开发者看的）

- **后端：** Python + FastAPI
- **数据库：** SQLite（默认）或 MySQL+libsql
- **前端：** Vue +TailwindCSS
- **部署：** Docker + Docker Compose
- **AI 对接：** OpenAI API（或兼容接口）

---

## 面向开发者

### 环境准备

- Python 3.10+（建议使用虚拟环境）
- Node.js 18+ 与 npm
- pip / virtualenv（或你习惯的依赖管理工具）
- 可选：Docker 与 Docker Compose（用于一键部署与发布）

### 后端本地开发

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

默认会监听 `http://127.0.0.1:8000`，你可以通过 `--host`、`--port` 调整，或加上 `--reload` 保持热重载。

### 前端本地开发

```bash
cd frontend
npm install
npm run dev
```

开发服务器默认运行在 `http://127.0.0.1:5173`，可通过 `--host` 参数暴露给局域网设备。

### 打包与构建

- 前端：`npm run build`，构建产物位于 `frontend/dist/`
- 后端：确认依赖锁定后，可使用 `pip install -r requirements.txt` 安装到目标环境，或基于 `deploy/Dockerfile` 构建镜像
- 静态文件托管：生产环境下可用 Nginx 等服务托管 `dist` 目录，并由后端提供 API

### 发布与部署

推荐在根目录下使用 Compose 文件完成一体化部署：

```bash
docker compose -f deploy/docker-compose.yml up -d --build
```

如需推送镜像，可在 `deploy` 目录执行 `docker build -t <registry>/arboris:<tag> .`，测试后再 `docker push` 发布。

---

## 参与贡献

如果你觉得这个项目有意思，欢迎：

- ⭐ 给个 Star
- 🐛 提 Bug 或建议（在 Issues 里）
- 💻 贡献代码（PR 我们都会认真看）
- 💬 加群聊天（二维码在最上面）

---

## 最后说两句

如果你用 Arboris 写出了什么有趣的东西，记得告诉我们。  

祝你写作顺利，故事精彩。





## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

[![Star History Chart](https://api.star-history.com/svg?repos=t59688/arboris-novel&type=Date)](https://star-history.com/#t59688/arboris-novel&Date)
