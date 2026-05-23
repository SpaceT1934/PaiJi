import cors from 'cors'
import dotenv from 'dotenv'
import express from 'express'
import multer from 'multer'

dotenv.config({ path: new URL('../.env', import.meta.url) })

const app = express()
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 },
})

app.use(
  cors({
    origin: true,
    credentials: false,
  }),
)

app.get('/health', (_req, res) => {
  res.json({ ok: true })
})

function requiredEnv(name) {
  const raw = process.env[name]
  const v = raw ? normalizeEnvValue(raw) : ''
  if (!v) {
    throw new Error(`Missing env: ${name}`)
  }
  return v
}

function normalizeEnvValue(v) {
  return String(v).trim().replace(/^`|`$/g, '').replace(/^"|"$/g, '').replace(/^'|'$/g, '')
}

function extractTextFromResponses(respJson) {
  if (typeof respJson?.output_text === 'string' && respJson.output_text.trim()) {
    return respJson.output_text
  }

  const out = respJson?.output
  if (!Array.isArray(out)) return ''

  const parts = []
  for (const item of out) {
    const content = item?.content
    if (typeof content === 'string' && content.trim()) parts.push(content)
    if (Array.isArray(content)) {
      for (const c of content) {
        if (typeof c?.text === 'string' && c.text.trim()) parts.push(c.text)
      }
    }
  }
  return parts.join('')
}

function buildUrl(base, path) {
  const baseWithSlash = base.endsWith('/') ? base : `${base}/`
  return new URL(path, baseWithSlash).toString()
}

function imageToDataUrl(file) {
  const mime = file.mimetype || 'image/jpeg'
  const base64 = file.buffer.toString('base64')
  return `data:${mime};base64,${base64}`
}

app.post('/api/card', upload.single('image'), async (req, res) => {
  try {
    const baseUrl = normalizeEnvValue(process.env.DEEPSEEK_BASE_URL || 'https://api.deepseek.com/v1')
    const model = normalizeEnvValue(process.env.DEEPSEEK_MODEL || 'deepseek-vl-chat')

    if (!req.file) {
      res.status(400).json({ error: 'Missing image file field: image' })
      return
    }

    const userHint = typeof req.body?.hint === 'string' ? req.body.hint : ''
    const imageUrl = imageToDataUrl(req.file)

    if (process.env.MOCK_AI === '1') {
      res.json({
        title: '测试卡片（MOCK_AI=1）',
        tags: ['mock', '本地调试', 'flipbook'],
        meme_top: '先把 UI 跑通',
        meme_bottom: userHint ? userHint.slice(0, 24) : '再接真·视觉模型',
        monologues: [
          '你以为我在看图？我在看你的执行力。',
          '先跑通流程就很棒了，下一步我们再变得更聪明。',
          '世界线收束：这张卡片会成为你们的第一章。',
        ],
        analysis: {
          objects: ['(mock)'],
          scene: '(mock)',
          mood: '(mock)',
        },
      })
      return
    }

    const apiKey = normalizeEnvValue(process.env.ARK_API_KEY || process.env.DEEPSEEK_API_KEY || '')
    if (!apiKey) {
      throw new Error('Missing env: DEEPSEEK_API_KEY (or ARK_API_KEY)')
    }

    const systemPrompt = [
      '你是一个“万物有梗”卡片生成器。',
      '你会看到一张用户拍的照片，请基于视觉理解生成一个可分享的卡片内容。',
      '你必须只输出 JSON（不要包含 markdown、不要多余解释）。',
      '',
      'JSON Schema：',
      '{',
      '  "title": string,',
      '  "tags": string[],',
      '  "meme_top": string,',
      '  "meme_bottom": string,',
      '  "monologues": [string, string, string],',
      '  "analysis": {',
      '    "objects": string[],',
      '    "scene": string,',
      '    "mood": string',
      '  }',
      '}',
      '',
      '约束：',
      '- monologues 必须是 3 种不同风格（毒舌/温柔/中二），每条 15-40 字。',
      '- meme_top + meme_bottom 适合做梗图配文，尽量简短有力。',
    ].join('\n')

    const userText = userHint ? `用户补充：${userHint}\n请生成卡片。` : '请生成卡片。'
    const upstreamMode = normalizeEnvValue(process.env.UPSTREAM_MODE || '')
    const useResponses = upstreamMode === 'responses' || baseUrl.includes('volces.com')

    const apiResp = await fetch(buildUrl(baseUrl, useResponses ? 'responses' : 'chat/completions'), {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(
        useResponses
          ? {
              model,
              input: [
                { role: 'system', content: systemPrompt },
                {
                  role: 'user',
                  content: [
                    { type: 'input_image', image_url: imageUrl },
                    { type: 'input_text', text: userText },
                  ],
                },
              ],
              text: { format: { type: 'json_object' } },
              temperature: 0.2,
              max_output_tokens: 900,
            }
          : {
              model,
              messages: [
                { role: 'system', content: systemPrompt },
                {
                  role: 'user',
                  content: [
                    { type: 'text', text: userText },
                    { type: 'image_url', image_url: { url: imageUrl } },
                  ],
                },
              ],
              temperature: 0.2,
              max_tokens: 900,
            },
      ),
    })

    const respText = await apiResp.text()
    if (!apiResp.ok) {
      if (respText.includes('unknown variant `image_url`')) {
        res.status(502).json({
          error: 'Upstream DeepSeek error',
          status: apiResp.status,
          detail: respText,
          hint: '当前上游接口不支持图片输入（image_url）。如果你用的是火山方舟/豆包，请在 server/.env 设置 UPSTREAM_MODE=responses；或先设置 MOCK_AI=1 跑通前端流程。',
        })
        return
      }
      res.status(502).json({
        error: 'Upstream DeepSeek error',
        status: apiResp.status,
        detail: respText,
      })
      return
    }

    const respJson = JSON.parse(respText)
    const content = useResponses ? extractTextFromResponses(respJson) : respJson?.choices?.[0]?.message?.content
    if (typeof content !== 'string' || !content.trim()) {
      res.status(502).json({ error: 'Invalid DeepSeek response', detail: respJson })
      return
    }

    let card
    try {
      card = JSON.parse(content)
    } catch {
      const firstBrace = content.indexOf('{')
      const lastBrace = content.lastIndexOf('}')
      if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
        card = JSON.parse(content.slice(firstBrace, lastBrace + 1))
      } else {
        throw new Error('Model output is not valid JSON')
      }
    }

    res.json(card)
  } catch (e) {
    res.status(500).json({ error: e?.message || String(e) })
  }
})

const port = Number(process.env.PORT || 8787)
app.listen(port, () => {
  console.log(`server listening on http://localhost:${port}`)
})
