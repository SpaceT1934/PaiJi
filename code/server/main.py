import argparse
import base64
import json
import os
import time
from typing import Any, Dict

import requests


BASE_URL_DEFAULT = "https://ark.cn-beijing.volces.com/api/v3"
CONFIG_DEFAULT = "card_from_image.local.json"


def require_env(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise RuntimeError(f"Missing env: {name}")
    return v


def load_local_config(path: str) -> Dict[str, Any]:
    p = path.strip()
    if not p or not os.path.exists(p):
        return {}
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def request_json(method: str, url: str, api_key: str, **kwargs) -> Dict[str, Any]:
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.request(method, url, headers=headers, timeout=120, **kwargs)
    if resp.status_code >= 400:
        raise RuntimeError(resp.text)
    return resp.json()


def upload_file(base_url: str, api_key: str, image_path: str) -> str:
    url = f"{base_url}/files"
    with open(image_path, "rb") as f:
        files = {"file": (os.path.basename(image_path), f, "application/octet-stream")}
        data = {"purpose": "user_data"}
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            files=files,
            data=data,
            timeout=120,
        )
    if resp.status_code >= 400:
        raise RuntimeError(resp.text)
    j = resp.json()
    file_id = j.get("id")
    if not file_id:
        raise RuntimeError(f"Invalid upload response: {j}")
    return file_id


def wait_for_processing(base_url: str, api_key: str, file_id: str, timeout_sec: int = 120) -> None:
    deadline = time.time() + timeout_sec
    while True:
        j = request_json("GET", f"{base_url}/files/{file_id}", api_key)
        status = str(j.get("status") or "").lower()
        if status in ("active", "processed", "succeeded", "success", "ready"):
            return
        if status in ("failed", "error"):
            raise RuntimeError(f"File processing failed: {j}")
        if time.time() > deadline:
            raise RuntimeError(f"Timeout waiting for file processing. Last status: {j}")
        time.sleep(1.0)


def extract_output_text(resp_json: Dict[str, Any]) -> str:
    ot = resp_json.get("output_text")
    if isinstance(ot, str) and ot.strip():
        return ot

    out = resp_json.get("output")
    if not isinstance(out, list):
        return ""

    parts = []
    for item in out:
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if isinstance(content, str) and content.strip():
            parts.append(content)
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and isinstance(c.get("text"), str) and c["text"].strip():
                    parts.append(c["text"])
    return "".join(parts)


def generate_card(
    base_url: str,
    api_key: str,
    model: str,
    file_id: str,
    hint: str = "",
) -> Dict[str, Any]:
    system_prompt = "\n".join(
        [
            "你是一个“卡片生成器”。你会看到用户上传的一张图片。",
            "请基于视觉理解生成一个可分享的卡片内容。",
            "输出必须是严格 JSON（不要 markdown，不要多余解释）。",
            "",
            "JSON Schema：",
            "{",
            '  "title": string,',
            '  "tags": string[],',
            '  "meme_top": string,',
            '  "meme_bottom": string,',
            '  "monologues": [string, string, string],',
            '  "analysis": {',
            '    "objects": string[],',
            '    "scene": string,',
            '    "mood": string',
            "  }",
            "}",
            "",
            "约束：",
            "- monologues 必须是 3 种不同风格（毒舌/温柔/中二），每条 15-40 字。",
            "- meme_top + meme_bottom 适合做梗图配文，尽量简短有力。",
        ]
    )

    user_text = f"用户补充：{hint}\n请生成卡片。" if hint else "请生成卡片。"

    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "input_image", "file_id": file_id},
                    {"type": "input_text", "text": user_text},
                ],
            },
        ],
        "text": {"format": {"type": "json_object"}},
        "thinking": {"type": "disabled"},
        "temperature": 0.2,
        "max_output_tokens": 1600,
    }

    resp_json = request_json("POST", f"{base_url}/responses", api_key, json=payload)
    text = extract_output_text(resp_json).strip()

    if not text and resp_json.get("status") == "incomplete":
        prev_id = resp_json.get("id")
        if prev_id:
            payload2 = {
                "model": model,
                "previous_response_id": prev_id,
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "继续。请只输出最终 JSON 对象，不要输出思考过程、不要输出多余文字。",
                            }
                        ],
                    }
                ],
                "text": {"format": {"type": "json_object"}},
                "thinking": {"type": "disabled"},
                "temperature": 0.2,
                "max_output_tokens": 1600,
            }
            resp_json = request_json("POST", f"{base_url}/responses", api_key, json=payload2)
            text = extract_output_text(resp_json).strip()

    if not text:
        raise RuntimeError(f"Empty model output: {resp_json}")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1 and last > first:
            return json.loads(text[first : last + 1])
        raise RuntimeError("Model output is not valid JSON")


def image_path_to_data_url(image_path: str) -> str:
    with open(image_path, "rb") as f:
        raw = f.read()
    ext = os.path.splitext(image_path)[1].lower()
    if ext in (".jpg", ".jpeg"):
        mime = "image/jpeg"
    elif ext == ".png":
        mime = "image/png"
    elif ext == ".webp":
        mime = "image/webp"
    else:
        mime = "application/octet-stream"
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


def render_card_html(card: Dict[str, Any], image_data_url: str) -> str:
    title = str(card.get("title") or "")
    tags = card.get("tags") if isinstance(card.get("tags"), list) else []
    tags = [str(t) for t in tags][:10]
    meme_top = str(card.get("meme_top") or "")
    meme_bottom = str(card.get("meme_bottom") or "")
    monologues = card.get("monologues") if isinstance(card.get("monologues"), list) else []
    monologues = [str(x) for x in monologues][:3]
    monologue_main = monologues[0] if monologues else ""

    tags_html = "".join([f'<span class="tag">{t}</span>' for t in tags])
    monos_html = "".join([f'<li class="monoItem">{m}</li>' for m in monologues])

    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <style>
      :root {{
        --bg: #0b0b10;
        --card: rgba(255,255,255,0.06);
        --border: rgba(255,255,255,0.12);
        --text: rgba(255,255,255,0.85);
        --text2: rgba(255,255,255,0.68);
        --shadow: rgba(0,0,0,0.45) 0 16px 50px;
      }}
      html, body {{
        height: 100%;
        margin: 0;
        background: radial-gradient(1200px 800px at 20% 10%, rgba(120,80,255,0.22), transparent 55%),
                    radial-gradient(900px 700px at 80% 90%, rgba(0,180,255,0.18), transparent 55%),
                    var(--bg);
        color: var(--text);
        font-family: system-ui, -apple-system, Segoe UI, Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
      }}
      .wrap {{
        min-height: 100%;
        display: grid;
        place-items: center;
        padding: 24px;
        box-sizing: border-box;
      }}
      .card {{
        width: min(520px, 100%);
        aspect-ratio: 3 / 4;
        border-radius: 18px;
        overflow: hidden;
        background: var(--card);
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        display: grid;
        grid-template-rows: 1fr auto;
      }}
      .image {{
        position: relative;
        background-image: url("{image_data_url}");
        background-size: cover;
        background-position: center;
      }}
      .overlay {{
        position: absolute;
        inset: 0;
        padding: 14px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        text-transform: uppercase;
        font-weight: 900;
        letter-spacing: 0.8px;
        color: rgba(255,255,255,0.95);
        text-shadow: rgba(0,0,0,0.75) 0 2px 14px;
      }}
      .memeTop, .memeBottom {{
        font-size: 28px;
        line-height: 1.08;
        word-break: break-word;
      }}
      .meta {{
        padding: 12px 14px 14px;
        border-top: 1px solid var(--border);
        background: linear-gradient(180deg, rgba(0,0,0,0.0), rgba(0,0,0,0.22));
        display: grid;
        gap: 10px;
      }}
      .title {{
        font-size: 16px;
        font-weight: 750;
      }}
      .tags {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
      }}
      .tag {{
        font-size: 12px;
        padding: 3px 8px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: rgba(255,255,255,0.04);
        color: var(--text2);
      }}
      .mono {{
        font-size: 13px;
        line-height: 1.4;
        color: var(--text2);
      }}
      .monoMain {{
        color: var(--text);
      }}
      .monoList {{
        margin: 0;
        padding-left: 18px;
        display: grid;
        gap: 6px;
      }}
      .monoItem {{
        color: var(--text2);
      }}
      .footer {{
        margin-top: 14px;
        width: min(520px, 100%);
        color: var(--text2);
        font-size: 12px;
        text-align: center;
        user-select: none;
      }}
      .btn {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        height: 34px;
        padding: 0 12px;
        margin-top: 10px;
        border-radius: 10px;
        border: 1px solid var(--border);
        background: rgba(255,255,255,0.05);
        color: var(--text);
        text-decoration: none;
      }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <div>
        <div class="card">
          <div class="image">
            <div class="overlay">
              <div class="memeTop">{meme_top}</div>
              <div class="memeBottom">{meme_bottom}</div>
            </div>
          </div>
          <div class="meta">
            <div class="title">{title}</div>
            <div class="tags">{tags_html}</div>
            <div class="mono">
              <div class="monoMain">{monologue_main}</div>
              <ul class="monoList">{monos_html}</ul>
            </div>
          </div>
        </div>
        <div class="footer">
          生成于本地脚本 · 可直接截图分享
          <div><a class="btn" download="card.json" href="data:application/json;charset=utf-8,{requests.utils.requote_uri(json.dumps(card, ensure_ascii=False))}">下载 JSON</a></div>
        </div>
      </div>
    </div>
  </body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=CONFIG_DEFAULT, help="本地配置文件路径")
    parser.add_argument("--image", default=os.getenv("IMAGE_PATH", "").strip(), help="本地图片路径")
    parser.add_argument("--hint", default="", help="可选：补充提示词")
    parser.add_argument("--base-url", default=BASE_URL_DEFAULT)
    parser.add_argument("--model", default=os.getenv("ARK_MODEL", "").strip(), help="方舟控制台已开通的模型ID")
    parser.add_argument("--out-html", default="card.html", help="输出可视化卡片 HTML 文件路径")
    parser.add_argument("--no-json", action="store_true", help="不在控制台输出 JSON")
    args = parser.parse_args()

    cfg = load_local_config(args.config)
    image_path = args.image or str(cfg.get("image") or "").strip()
    model = args.model or str(cfg.get("model") or "").strip()
    hint = args.hint or str(cfg.get("hint") or "").strip()
    out_html = args.out_html or str(cfg.get("out_html") or "").strip()
    base_url = (args.base_url or str(cfg.get("base_url") or BASE_URL_DEFAULT)).strip().rstrip("/")

    api_key = os.getenv("ARK_API_KEY", "").strip() or str(cfg.get("api_key") or "").strip()

    if not image_path:
        raise SystemExit('Missing --image (or env IMAGE_PATH or config.image)')
    if not model:
        raise SystemExit('Missing --model (or env ARK_MODEL or config.model)')
    if not api_key:
        raise SystemExit('Missing ARK_API_KEY (env ARK_API_KEY or config.api_key)')

    file_id = upload_file(base_url, api_key, image_path)
    wait_for_processing(base_url, api_key, file_id)

    card = generate_card(base_url, api_key, model, file_id, hint=hint)
    if not args.no_json:
        print(json.dumps(card, ensure_ascii=False, indent=2))

    if out_html:
        html = render_card_html(card, image_path_to_data_url(image_path))
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Wrote HTML: {os.path.abspath(out_html)}")


if __name__ == "__main__":
    main()
