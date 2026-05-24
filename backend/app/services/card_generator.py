import base64
import json
import re
from typing import Any

import requests

from app.core.config import settings


def image_bytes_to_data_url(raw: bytes, mime: str) -> str:
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{mime or 'image/jpeg'};base64,{encoded}"


def build_url(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def extract_response_text(resp_json: dict[str, Any]) -> str:
    output_text = resp_json.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    output = resp_json.get("output")
    if not isinstance(output, list):
        return ""

    parts: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if isinstance(content, str) and content.strip():
            parts.append(content)
        elif isinstance(content, list):
            for piece in content:
                if isinstance(piece, dict) and isinstance(piece.get("text"), str):
                    parts.append(piece["text"])
    return "".join(parts)


def parse_json_object(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        first = text.find("{")
        last = text.rfind("}")
        if first == -1 or last == -1 or last <= first:
            raise ValueError("Model output is not valid JSON") from None
        data = json.loads(text[first : last + 1])

    if not isinstance(data, dict):
        raise ValueError("Model output JSON must be an object")
    return data


def card_from_text(text: str, hint: str = "") -> dict[str, Any]:
    compact = " ".join((text or "").split())
    if not compact:
        return mock_card(hint)
    title_match = re.search(r'"title"\s*:\s*"([^"]+)"', compact)
    tags_match = re.search(r'"tags"\s*:\s*\[([^\]]+)\]', compact)
    text_match = re.search(r'"text"\s*:\s*"([^"]+)"', compact)
    meme_bottom_match = re.search(r'"meme_bottom"\s*:\s*"([^"]+)"', compact)
    extracted_tags = []
    if tags_match:
        extracted_tags = [item.strip().strip('"') for item in tags_match.group(1).split(",") if item.strip()]
    readable = text_match.group(1) if text_match else meme_bottom_match.group(1) if meme_bottom_match else ""
    if not readable or compact.lstrip().startswith("{"):
        readable = f"AI 已读取这张照片，并把它整理成《{hint or '旅行手账'}》里的新卡片。"
    return {
        "title": title_match.group(1) if title_match else hint or "新生成的旅行卡片",
        "tags": [
            {"label": tag, "popupText": f"{tag} 是这张照片里值得被记住的小线索。"}
            for tag in (extracted_tags[:3] or ["AI 观察", "旅行手账", "临时卡片"])
        ],
        "meme_top": "照片已读",
        "meme_bottom": "先贴进手账再说",
        "monologues": [
            readable[:80],
            "这张照片像一枚现场留下的小票据，被 AI 贴进了旅途里。",
            "地图节点亮起，一张新的手账入口正在生成。",
        ],
        "analysis": {
            "objects": [],
            "scene": hint or "travel moment",
            "mood": "observed",
        },
        "category": "照片",
        "text": readable[:120],
        "next_prompt": "再拍一张同一地点的细节，我会继续补成新的手账卡片。",
        "hotspots": [],
    }


def mock_card(hint: str = "") -> dict[str, Any]:
    return {
        "title": "刚刚生成的旅行贴纸",
        "tags": [
            {"label": "📷 新照片", "popupText": "这张照片会先变成一张独立手账卡片。"},
            {"label": "🧭 旅行线索", "popupText": "AI 会把画面里的地点、物件和氛围整理出来。"},
            {"label": "✍️ 手账贴纸", "popupText": "它会被贴到当前地点的手账画布里。"},
        ],
        "meme_top": "照片一来",
        "meme_bottom": "手账就有了新入口",
        "monologues": [
            "这张照片先不存服务器，只在这次体验里变成贴纸。",
            "把眼前的一瞬间，轻轻贴进这本旅行书。",
            "此刻，地图和手账完成了一次小小的世界线合流。",
        ],
        "analysis": {
            "objects": ["photo"],
            "scene": hint or "travel moment",
            "mood": "warm scrapbook",
        },
        "category": "照片",
        "text": "AI 已根据照片生成一张临时手账卡片，可作为画布上的贴纸入口。",
        "next_prompt": "继续视觉搜索：拍一张你最想补充的细节。",
        "hotspots": [],
    }


def normalize_tags(tags: Any) -> list[dict[str, str]]:
    if not isinstance(tags, list):
        return []
    normalized: list[dict[str, str]] = []
    for item in tags[:3]:
        if isinstance(item, dict):
            label = str(item.get("label") or item.get("name") or "").strip()
            popup = str(item.get("popupText") or item.get("popup") or item.get("text") or "").strip()
        else:
            label = str(item).strip()
            popup = ""
        if not label:
            continue
        normalized.append(
            {
                "label": label,
                "popupText": popup or f"{label} 是这张照片里被 AI 捕捉到的旅行线索。",
            }
        )
    return normalized


def normalize_card(card: dict[str, Any]) -> dict[str, Any]:
    monologues = card.get("monologues")
    text = ""
    if isinstance(monologues, list) and monologues:
        text = str(monologues[0])
    text = str(card.get("text") or text or card.get("meme_bottom") or "")

    tags = normalize_tags(card.get("tags"))

    return {
        "title": str(card.get("title") or "新生成的手账卡片"),
        "tags": tags,
        "meme_top": str(card.get("meme_top") or ""),
        "meme_bottom": str(card.get("meme_bottom") or ""),
        "monologues": [str(item) for item in monologues[:3]] if isinstance(monologues, list) else [],
        "analysis": card.get("analysis") if isinstance(card.get("analysis"), dict) else {},
        "category": str(card.get("category") or "照片"),
        "text": text,
        "next_prompt": str(card.get("next_prompt") or card.get("nextPrompt") or "再拍一张相关细节，我会继续补成新的手账卡片。"),
        "hotspots": card.get("hotspots") if isinstance(card.get("hotspots"), list) else [],
    }


def generate_card_from_image(image: bytes, mime: str, hint: str = "") -> dict[str, Any]:
    if settings.mock_ai or not settings.api_key:
        return normalize_card(mock_card(hint))

    image_url = image_bytes_to_data_url(image, mime)
    system_prompt = "\n".join(
        [
            "你是一个旅行手账卡片生成器。",
            "你会看到用户拍摄的一张照片，请基于视觉理解生成一个适合放进旅行手账 canvas 的卡片内容。",
            "你必须只输出 JSON，不要 markdown，不要多余解释。",
            "",
            "JSON Schema:",
            "{",
            '  "title": string,',
            '  "tags": [{ "label": string, "popupText": string }],',
            '  "meme_top": string,',
            '  "meme_bottom": string,',
            '  "monologues": [string, string, string],',
            '  "analysis": { "objects": string[], "scene": string, "mood": string },',
            '  "category": string,',
            '  "text": string,',
            '  "next_prompt": string,',
            '  "hotspots": [{ "label": string, "x": number, "y": number, "popupText": string }]',
            "}",
            "",
            "约束：",
            "- category 从 美食/文物/小动物/风景/街景/人物/照片 中选一个。",
            "- title 是一句有趣、有情绪的话，16 字以内，例如“这只猫比我还会享受旅行”。",
            "- tags 必须正好 3 个，每个 label 都是视觉搜索入口，格式为“搜身份：.../搜附近：.../搜故事：...”，popupText 是搜索结果解释，20-45 字。",
            "- next_prompt 必须以“继续视觉搜索：”开头，引导用户继续拍照，例如“继续视觉搜索：拍它看向的方向”。",
            "- hotspots 给 1-2 个照片内可点击线索，x/y 为百分比坐标 10-90，label 以“搜...”开头。",
            "- text 是适合贴在牛皮纸手账上的短文案，30-60 字。",
            "- monologues 必须是 3 种不同风格（毒舌/温柔/中二），每条 15-40 字。",
            "- 不要编造确定事实；不确定时用观察性的描述。",
            "- JSON 必须完整闭合，所有字符串必须闭合。",
        ]
    )
    user_text = f"用户补充：{hint}\n请生成卡片。" if hint else "请生成卡片。"

    use_responses = settings.upstream_mode == "responses" or "volces.com" in settings.api_base_url
    if use_responses:
        payload: dict[str, Any] = {
            "model": settings.model,
            "input": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_image", "image_url": image_url},
                        {"type": "input_text", "text": user_text},
                    ],
                },
            ],
            "text": {"format": {"type": "json_object"}},
            "temperature": 0.2,
            "max_output_tokens": 2000,
        }
        endpoint = build_url(settings.api_base_url, "responses")
    else:
        payload = {
            "model": settings.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
            "temperature": 0.2,
            "max_tokens": 2000,
        }
        endpoint = build_url(settings.api_base_url, "chat/completions")

    resp = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {settings.api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    if resp.status_code >= 400:
        raise RuntimeError(resp.text)

    resp_json = resp.json()
    content = extract_response_text(resp_json) if use_responses else resp_json["choices"][0]["message"]["content"]
    try:
        parsed = parse_json_object(content)
    except ValueError:
        parsed = card_from_text(content, hint)
    return normalize_card(parsed)
