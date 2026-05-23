# card_from_image

主入口：`main.py`

## 安装

```bash
pip install -r requirements.txt
```

## 配置（不要提交密钥）

方式 1：环境变量（推荐）

```bash
set ARK_API_KEY=你的key
set ARK_MODEL=你的模型ID
```

方式 2：本地配置文件

复制示例并填入本地密钥：

```bash
copy card_from_image.example.json card_from_image.local.json
```

## 运行

```bash
python main.py --image path/to/your.jpg --model 你的模型ID
```

输出：默认生成 `card.html`（已在 `.gitignore` 中忽略）
