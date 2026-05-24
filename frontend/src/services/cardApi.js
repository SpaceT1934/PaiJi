const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8787"

export async function generateCardFromImage(file, hint = "") {
  const form = new FormData()
  form.append("image", file)
  form.append("hint", hint)
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), 45000)

  let response
  try {
    response = await fetch(`${API_BASE_URL}/api/cards/generate`, {
      method: "POST",
      body: form,
      signal: controller.signal
    })
  } finally {
    window.clearTimeout(timeoutId)
  }

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Card API failed: ${response.status}`)
  }

  return response.json()
}
