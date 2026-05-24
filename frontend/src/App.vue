<script setup>
import { computed, ref } from "vue"
import BottomTabBar from "./components/BottomTabBar.vue"
import CommunityPage from "./pages/CommunityPage.vue"
import CreateBookPage from "./pages/GeneratePage.vue"
import BookDetailPage from "./pages/JournalPage.vue"
import HomePage from "./pages/HomePage.vue"
import { generateCardFromImage } from "./services/cardApi.js"

const screen = ref("home")
const toast = ref("")
const bookTitle = ref("南京周末漫游")
const generatedCards = ref([])
const placeCards = ref({
  fuzimiao: [
    {
      id: "fuzimiao-cat",
      name: "夫子庙线索",
      placeId: "fuzimiao",
      lat: 32.022579,
      lng: 118.783786,
      image: "/tripnote/assets/fuzimiao-cat-guide.jpg",
      title: "这只猫可能才是夫子庙的夜班向导",
      text: "夜色刚落下时，它蹲在灯影边，像是在等一个迟到的游客。你顺着它的目光抬头，夫子庙的灯火就从巷口慢慢亮了起来。",
      category: "拍摄引导卡",
      tone: "#f0d8c7",
      tags: [
        { label: "夜班猫", popupText: "它像是老街里最熟路的本地向导，安静地守着人来人往的路口。" },
        { label: "暖色灯光", popupText: "背后的暖光把街巷烘得很软，也把下一段夜游的方向照出来。" },
        { label: "谁在带路", popupText: "这一页从猫的眼神开始，像一条小小的线，把你牵进夫子庙的夜里。" }
      ],
      hotspots: [
        { label: "拍猫看向的方向", x: 62, y: 42, nextCardId: "fuzimiao-lantern", popupText: "下一张可以拍它看向的灯光，让故事从猫的眼神走进夜市。" },
        { label: "拍脚下石板", x: 42, y: 76, nextCardId: "fuzimiao-stone", popupText: "也可以低头拍脚下的石板，把故事带到老街更安静的一面。" }
      ],
      nextPrompt: "拍一下它看向的方向",
      capturedAt: "2026-05-24T19:10:00+08:00"
    },
    {
      id: "fuzimiao-lantern",
      name: "夫子庙线索",
      placeId: "fuzimiao",
      lat: 32.022579,
      lng: 118.783786,
      image: "/tripnote/assets/fuzimiao-lantern-crowd.jpg",
      title: "猫把你带到了夜色的开关下面",
      text: "灯笼一盏盏亮起来，人群从桥边慢慢涌过。刚才那只猫像是把你带到了夜游真正开始的地方，空气里也多了一点甜甜的热气。",
      category: "下一页引导卡",
      tone: "#e6d8b8",
      tags: [
        { label: "夜游开关", popupText: "暖色灯笼一亮，普通街景就变成了可以被记住的夜晚。" },
        { label: "人群方向", popupText: "人流方向往往指向小吃摊、牌坊或河边入口，适合继续拍摄。" },
        { label: "灯下有人", popupText: "灯笼下的人影让故事从物件进入人物，热闹也就有了温度。" }
      ],
      hotspots: [
        { label: "拍灯下人群", x: 46, y: 28, nextCardId: "fuzimiao-food", popupText: "下一张可以拍灯下经过的人，让夜游从风景变成有人情味的片段。" },
        { label: "拍旁边小吃摊", x: 72, y: 70, nextCardId: "fuzimiao-food", popupText: "也可以把镜头转向摊位，记录这条街真正的烟火气。" }
      ],
      nextPrompt: "拍一下灯下的人群",
      capturedAt: "2026-05-24T19:14:00+08:00"
    },
    {
      id: "fuzimiao-food",
      name: "夫子庙线索",
      placeId: "fuzimiao",
      lat: 32.022579,
      lng: 118.783786,
      image: "/tripnote/assets/fuzimiao-night-snack.jpg",
      title: "一碗热气腾腾的南京夜晚",
      text: "从猫的视线到灯笼的暖光，故事最后落在这碗夜宵上。热气升起来的时候，整条街都像慢了一拍，旅行也突然有了味道。",
      category: "故事延展卡",
      tone: "#d9e3e1",
      tags: [
        { label: "夜市热气", popupText: "热气、碗沿和暖光共同构成了这条故事线的烟火气终点。" },
        { label: "从猫到灯", popupText: "这条路线让几张随手拍不再孤立，而是变成一段能翻下去的夜游。" },
        { label: "桌边细节", popupText: "如果继续拍桌上的票据、杯子或菜单，故事还能展开成下一页。" }
      ],
      hotspots: [
        { label: "拍菜单或票据", x: 30, y: 34, nextCardId: "fuzimiao-stone", popupText: "下一张可以拍菜单、票据或店名，把这一碗夜宵变成有出处的记忆。" },
        { label: "拍桌边细节", x: 58, y: 42, nextCardId: "fuzimiao-stone", popupText: "也可以拍碗沿、筷子和热气，让这页手账更有现场感。" }
      ],
      nextPrompt: "拍一下菜单或票据",
      capturedAt: "2026-05-24T19:18:00+08:00"
    },
    {
      id: "fuzimiao-stone",
      name: "夫子庙线索",
      placeId: "fuzimiao",
      lat: 32.022579,
      lng: 118.783786,
      image: "/tripnote/assets/fuzimiao-stone-texture.jpg",
      title: "老街纹理把故事带回了城市记忆",
      text: "热闹走远之后，脚下的石板还留着湿润的光。青苔、砖缝和旧墙，把夫子庙安静的一面留了下来，像这趟夜游的最后一页。",
      category: "支线引导卡",
      tone: "#e6d8b8",
      tags: [
        { label: "石板路", popupText: "石板的磨损痕迹是城市使用过的证据，比标准景点更有个人记忆。" },
        { label: "旧墙颜色", popupText: "旧墙的颜色能提示湿度、年代感和街区气质。" },
        { label: "低头路线", popupText: "这是一条反游客路线：不看招牌，专门看脚下和墙边。" }
      ],
      hotspots: [
        { label: "回到夜班猫", x: 52, y: 62, nextCardId: "fuzimiao-cat", popupText: "这条故事线可以回到开头，再从那只猫开始另一段路线。" }
      ],
      nextPrompt: "拍一块更旧的墙",
      capturedAt: "2026-05-24T19:22:00+08:00"
    }
  ]
})
const selectedLandmarkId = ref("")
const openingBook = ref(false)
const capturePanelOpen = ref(false)
const capturePlaceId = ref("fuzimiao")
const panelCameraInput = ref(null)
const panelAlbumInput = ref(null)
const sharePanelOpen = ref(false)
const sharePayload = ref(null)
const shareImageUrl = ref("")
const shareImageLoading = ref(false)
const cardGeneration = ref({
  active: false,
  total: 0,
  done: 0,
  failed: 0,
  source: "camera",
  visualProgress: 0,
  messageIndex: 0
})
let toastTimer
let generationProgressTimer
let generationMessageTimer

const activeScreen = computed(() => (screen.value === "profile" ? "home" : screen.value))
const mapBounds = {
  north: 32.09,
  south: 32.0,
  west: 118.74,
  east: 118.84
}

const baseCards = [
  {
    id: "city-wall",
    name: "明城墙",
    lat: 32.064313,
    lng: 118.791472,
    displayPosition: { x: 31, y: 45 },
    title: "城墙砖色里的开场",
    text: "城砖红、树影绿和古城轮廓很适合放在这本旅行书的第一站。",
    image: "https://images.unsplash.com/photo-1591120578245-5c6b79ab9c05?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=700",
    tone: "#e6d8b8"
  },
  {
    id: "jimingsi",
    name: "鸡鸣寺",
    lat: 32.062583,
    lng: 118.79023,
    displayPosition: { x: 70, y: 58 },
    title: "黄墙边的一次停顿",
    text: "寺庙的暖黄色和屋檐线条很明显，适合生成一页安静的章节卡片。",
    image: "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=700",
    tone: "#eeddb5"
  },
  {
    id: "xuanwu",
    name: "玄武湖",
    lat: 32.07123,
    lng: 118.79555,
    displayPosition: { x: 72, y: 32 },
    title: "湖边风把路线放慢",
    text: "水面和树影让这张卡片更像旅程里的呼吸页，适合连接城市和自然。",
    image: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=700",
    tone: "#d9e3e1"
  },
  {
    id: "fuzimiao",
    name: "夫子庙",
    lat: 32.022579,
    lng: 118.783786,
    displayPosition: { x: 37, y: 77 },
    title: "灯影里的烟火气",
    text: "这里适合成为夜游节点，灯光、人流和小吃会自然串成一页城市味道。",
    image: "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=700",
    tone: "#f0cdbf"
  }
]

function gpsToMap(lat, lng) {
  const x = ((lng - mapBounds.west) / (mapBounds.east - mapBounds.west)) * 100
  const y = ((mapBounds.north - lat) / (mapBounds.north - mapBounds.south)) * 100
  return {
    x: Math.min(88, Math.max(12, x)),
    y: Math.min(84, Math.max(14, y))
  }
}

const landmarks = computed(() =>
  [...baseCards, ...generatedCards.value].map((card) => ({
    ...card,
    cards: placeCards.value[card.id] || [],
    ...gpsToMap(card.lat, card.lng),
    ...(card.displayPosition || {})
  }))
)
const totalCardCount = computed(() =>
  landmarks.value.length + Object.values(placeCards.value).reduce((sum, cards) => sum + cards.length, 0)
)
const generationPercent = computed(() => {
  return Math.round(cardGeneration.value.visualProgress || 0)
})
const generationTitle = computed(() => {
  if (cardGeneration.value.source === "camera") return "正在生成拍照卡片"
  return `正在生成 ${cardGeneration.value.total} 张卡片`
})
const generationMessages = [
  "正在识别照片里的主角和场景",
  "正在提取适合贴进手账的颜色",
  "正在为这张照片写旅行旁白",
  "正在整理标签、位置和卡片入口",
  "快好了，正在把卡片贴进这本书"
]
const generationSubtitle = computed(() => {
  if (!cardGeneration.value.total) return "正在后台整理照片"
  const failedText = cardGeneration.value.failed ? `，${cardGeneration.value.failed} 张使用备用卡片` : ""
  return `${generationMessages[cardGeneration.value.messageIndex]} · 已完成 ${cardGeneration.value.done}/${cardGeneration.value.total}${failedText}`
})
const shareCopy = computed(() => {
  if (sharePayload.value?.type === "card") {
    return `我用拍迹生成了一张旅行手账卡片：${sharePayload.value.title}。#拍迹 #旅行手账`
  }
  const place = landmarks.value.find((item) => item.id === selectedLandmarkId.value)
  const placeText = place ? ` · ${place.name}` : ""
  return `我用拍迹把${bookTitle.value}${placeText}做成了一本会说话的旅行手账。#拍迹 #旅行手账 #南京周末漫游`
})

function startGenerationUi(total, source) {
  window.clearInterval(generationProgressTimer)
  window.clearInterval(generationMessageTimer)
  cardGeneration.value = {
    active: true,
    total,
    done: 0,
    failed: 0,
    source,
    visualProgress: 8,
    messageIndex: 0
  }

  generationProgressTimer = window.setInterval(() => {
    if (!cardGeneration.value.active) return
    const cap = cardGeneration.value.done >= cardGeneration.value.total ? 100 : 90
    const gap = cap - cardGeneration.value.visualProgress
    if (gap <= 0.4) return
    cardGeneration.value.visualProgress = Math.min(cap, cardGeneration.value.visualProgress + Math.max(0.45, gap * 0.055))
  }, 260)

  generationMessageTimer = window.setInterval(() => {
    if (!cardGeneration.value.active) return
    cardGeneration.value.messageIndex = (cardGeneration.value.messageIndex + 1) % generationMessages.length
  }, 2200)
}

function finishGenerationUi() {
  cardGeneration.value.visualProgress = 100
  window.clearInterval(generationProgressTimer)
  window.clearInterval(generationMessageTimer)
  window.setTimeout(() => {
    cardGeneration.value.active = false
  }, 900)
}

function showToast(message) {
  toast.value = message
  window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    toast.value = ""
  }, 1800)
}

async function copyShareText() {
  const text = shareCopy.value
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      fallbackCopy(text)
    }
    showToast("分享文案已复制")
  } catch {
    try {
      fallbackCopy(text)
      showToast("分享文案已复制")
    } catch {
      showToast("复制失败，请手动复制文案")
    }
  }
}

function fallbackCopy(text) {
  const textarea = document.createElement("textarea")
  textarea.value = text
  textarea.setAttribute("readonly", "")
  textarea.style.position = "fixed"
  textarea.style.left = "-9999px"
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand("copy")
  document.body.removeChild(textarea)
}

function downloadShareImage() {
  if (!shareImageUrl.value) return
  const link = document.createElement("a")
  link.href = shareImageUrl.value
  link.download = sharePayload.value?.filename || "tripnote-share.png"
  link.click()
  showToast("PNG 图片已保存")
}

async function openSharePanel(payload = null) {
  const place = landmarks.value.find((item) => item.id === selectedLandmarkId.value)
  sharePayload.value = payload || {
    type: "book",
    title: `${bookTitle.value}地图`,
    subtitle: place ? place.name : `${landmarks.value.length} 个 GPS 地标`,
    body: place?.text || "把一次旅行的照片整理成一本可以翻阅的旅行手账。",
    image: "/tripnote/assets/nanjing_map.png",
    tags: [{ label: "📍 地图" }, { label: "📖 旅行书" }, { label: "✍️ 手账" }],
    watermark: "拍迹 TripNote",
    filename: "tripnote-map.png"
  }
  sharePanelOpen.value = true
  shareImageLoading.value = true
  shareImageUrl.value = ""
  try {
    shareImageUrl.value = await createSharePng(sharePayload.value)
  } finally {
    shareImageLoading.value = false
  }
}

async function createSharePng(payload) {
  const canvas = document.createElement("canvas")
  canvas.width = 900
  canvas.height = 1200
  const ctx = canvas.getContext("2d")

  drawShareBackground(ctx, canvas.width, canvas.height)
  if (payload.type === "card") {
    await drawCardShare(ctx, payload)
  } else {
    await drawBookShare(ctx, payload)
  }
  return canvas.toDataURL("image/png")
}

function drawShareBackground(ctx, width, height) {
  const gradient = ctx.createLinearGradient(0, 0, width, height)
  gradient.addColorStop(0, "#fff8ea")
  gradient.addColorStop(1, "#ead7b7")
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, height)
  ctx.fillStyle = "rgba(36, 90, 85, 0.1)"
  ctx.beginPath()
  ctx.arc(780, 160, 96, 0, Math.PI * 2)
  ctx.fill()
  ctx.fillStyle = "rgba(185, 78, 59, 0.1)"
  ctx.beginPath()
  ctx.arc(118, 980, 128, 0, Math.PI * 2)
  ctx.fill()
}

async function drawCardShare(ctx, payload) {
  roundedRect(ctx, 88, 72, 724, 1056, 44)
  ctx.fillStyle = "#ffffff"
  ctx.fill()

  await drawImageCover(ctx, payload.image, 118, 108, 664, 560, 28)
  ctx.fillStyle = "#245a55"
  ctx.font = "700 28px sans-serif"
  ctx.fillText(payload.subtitle || "旅行故事卡", 126, 730)
  ctx.fillStyle = "#2f3329"
  ctx.font = "900 54px sans-serif"
  wrapText(ctx, payload.title || "旅行手账卡片", 126, 805, 648, 62, 2)
  ctx.fillStyle = "rgba(47, 51, 41, 0.78)"
  ctx.font = "700 30px sans-serif"
  wrapText(ctx, payload.body || "", 126, 925, 648, 46, 3)
  drawTags(ctx, payload.tags || [], 126, 1018)
  drawWatermark(ctx, payload.watermark || "拍迹 TripNote")
}

async function drawBookShare(ctx, payload) {
  roundedRect(ctx, 78, 86, 744, 1028, 42)
  ctx.fillStyle = "rgba(255,255,255,0.84)"
  ctx.fill()
  await drawImageCover(ctx, payload.image, 118, 134, 664, 520, 28)
  ctx.fillStyle = "#245a55"
  ctx.font = "800 34px sans-serif"
  ctx.fillText("拍迹 TripNote", 118, 724)
  ctx.fillStyle = "#2f3329"
  ctx.font = "900 58px sans-serif"
  wrapText(ctx, payload.title || "旅行书地图", 118, 808, 664, 66, 2)
  ctx.fillStyle = "#6f604c"
  ctx.font = "700 30px sans-serif"
  ctx.fillText(payload.subtitle || "旅行手账", 118, 940)
  ctx.fillStyle = "rgba(47, 51, 41, 0.78)"
  ctx.font = "700 28px sans-serif"
  wrapText(ctx, payload.body || "", 118, 1000, 664, 42, 2)
  drawWatermark(ctx, payload.watermark || "拍迹 TripNote")
}

function drawTags(ctx, tags, x, y) {
  let cursor = x
  ;(tags.length ? tags : [{ label: "✨ 故事" }, { label: "📍 旅行" }, { label: "✍️ 手账" }]).slice(0, 3).forEach((tag) => {
    const label = tag.label || String(tag)
    ctx.font = "700 24px sans-serif"
    const width = ctx.measureText(label).width + 38
    roundedRect(ctx, cursor, y, width, 48, 24)
    ctx.fillStyle = "rgba(36, 90, 85, 0.12)"
    ctx.fill()
    ctx.fillStyle = "#245a55"
    ctx.fillText(label, cursor + 19, y + 32)
    cursor += width + 12
  })
}

function drawWatermark(ctx, text) {
  ctx.fillStyle = "#b94e3b"
  ctx.font = "800 26px sans-serif"
  ctx.fillText(text, 118, 1078)
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight, maxLines = 3) {
  const words = String(text).split("")
  let line = ""
  let lines = 0
  for (const word of words) {
    const testLine = line + word
    if (ctx.measureText(testLine).width > maxWidth && line) {
      ctx.fillText(line, x, y)
      line = word
      y += lineHeight
      lines += 1
      if (lines >= maxLines) return
    } else {
      line = testLine
    }
  }
  if (line && lines < maxLines) ctx.fillText(line, x, y)
}

async function drawImageCover(ctx, src, x, y, width, height, radius) {
  roundedRect(ctx, x, y, width, height, radius)
  ctx.fillStyle = "#efe0c8"
  ctx.fill()
  if (!src) return
  try {
    const image = await loadImage(src)
    ctx.save()
    roundedRect(ctx, x, y, width, height, radius)
    ctx.clip()
    const scale = Math.max(width / image.width, height / image.height)
    const drawWidth = image.width * scale
    const drawHeight = image.height * scale
    ctx.drawImage(image, x + (width - drawWidth) / 2, y + (height - drawHeight) / 2, drawWidth, drawHeight)
    ctx.restore()
  } catch {
    ctx.fillStyle = "#245a55"
    ctx.font = "800 36px sans-serif"
    ctx.fillText("旅行书地图", x + 36, y + 82)
  }
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const image = new Image()
    if (!src.startsWith("blob:") && !src.startsWith("data:")) image.crossOrigin = "anonymous"
    image.onload = () => resolve(image)
    image.onerror = reject
    image.src = src
  })
}

function roundedRect(ctx, x, y, width, height, radius) {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
  ctx.lineTo(x + width, y + height - radius)
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
  ctx.lineTo(x + radius, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
  ctx.lineTo(x, y + radius)
  ctx.quadraticCurveTo(x, y, x + radius, y)
  ctx.closePath()
}

function openPlatform(platform) {
  const urls = {
    xiaohongshu: "xhsdiscover://",
    douyin: "snssdk1128://"
  }
  window.location.href = urls[platform]
  showToast(platform === "xiaohongshu" ? "正在尝试打开小红书" : "正在尝试打开抖音")
}

function changeScreen(target) {
  if (target === "profile") {
    showToast("我的暂未开放")
    return
  }

  screen.value = target
}

function createCard(file, index, aiCard = null, placeId = "") {
  const url = URL.createObjectURL(file)
  const titles = ["新拍到的南京瞬间", "街角新页", "旅行书的新一页", "刚刚加入的画面"]
  const colors = ["#dfe9d7", "#f0d8c7", "#e6d8b8", "#d9e3e1"]
  const fallbackGps = [
    [32.0428, 118.7842],
    [32.068, 118.807],
    [32.031, 118.778],
    [32.052, 118.818]
  ][(generatedCards.value.length + index) % 4]
  return {
    id: `${Date.now()}-${file.name}-${index}`,
    name: "新增地点",
    placeId,
    lat: fallbackGps[0],
    lng: fallbackGps[1],
    url,
    image: url,
    title: aiCard?.title || titles[(generatedCards.value.length + index) % titles.length],
    tone: colors[(generatedCards.value.length + index) % colors.length],
    text: aiCard?.text || aiCard?.monologues?.[0] || "这张照片已经被整理成当前旅行书里的新卡片。",
    tags: aiCard?.tags || [],
    hotspots: aiCard?.hotspots || [],
    category: aiCard?.category || "照片",
    nextPrompt: aiCard?.next_prompt || aiCard?.nextPrompt || "再拍一张相关细节",
    capturedAt: new Date().toISOString()
  }
}

function enrichCard(card, aiCard = null) {
  if (!aiCard) return card
  return {
    ...card,
    title: aiCard.title || card.title,
    text: aiCard.text || aiCard.monologues?.[0] || card.text,
    tags: aiCard.tags || card.tags,
    hotspots: aiCard.hotspots || card.hotspots,
    category: aiCard.category || card.category,
    nextPrompt: aiCard.next_prompt || aiCard.nextPrompt || card.nextPrompt
  }
}

function insertCard(card, targetPlaceId = "") {
  if (targetPlaceId) {
    placeCards.value = {
      ...placeCards.value,
      [targetPlaceId]: [card, ...(placeCards.value[targetPlaceId] || [])]
    }
    return
  }
  generatedCards.value = [card, ...generatedCards.value]
}

function updateCard(updatedCard, targetPlaceId = "") {
  if (targetPlaceId) {
    placeCards.value = {
      ...placeCards.value,
      [targetPlaceId]: (placeCards.value[targetPlaceId] || []).map((card) =>
        card.id === updatedCard.id ? updatedCard : card
      )
    }
    return
  }
  generatedCards.value = generatedCards.value.map((card) => (card.id === updatedCard.id ? updatedCard : card))
}

async function addPhotos(files, source = "camera", options = {}) {
  const list = Array.from(files || []).filter((file) => file.type.startsWith("image/"))
  if (!list.length) {
    showToast("还没有选择照片")
    return
  }

  screen.value = "book"
  const targetPlaceId = options.landmarkId || capturePlaceId.value || ""
  if (targetPlaceId) {
    selectedLandmarkId.value = targetPlaceId
  } else {
    selectedLandmarkId.value = ""
  }
  capturePanelOpen.value = false
  startGenerationUi(list.length, source)
  showToast(source === "camera" ? "已放入后台生成" : `${list.length} 张照片已放入后台生成`)

  await Promise.all(
    list.map(async (file, index) => {
      const card = createCard(file, index, null, targetPlaceId)
      insertCard(card, targetPlaceId)

      try {
        const aiCard = await generateCardFromImage(file, `${bookTitle.value} 旅行手账`)
        updateCard(enrichCard(card, aiCard), targetPlaceId)
      } catch (error) {
        console.warn("Card API fallback:", error)
        cardGeneration.value.failed += 1
      }
      cardGeneration.value.done += 1
    })
  )

  finishGenerationUi()
  const targetText = targetPlaceId ? "手账" : "地图"
  showToast(source === "camera" ? `拍照卡片已加入${targetText}` : `${list.length} 张卡片已加入${targetText}`)
}

function openCapturePanel() {
  capturePanelOpen.value = true
}

function triggerPanelCamera() {
  panelCameraInput.value?.click()
}

function triggerPanelAlbum() {
  panelAlbumInput.value?.click()
}

function handlePanelFiles(event, source) {
  addPhotos(event.target.files, source, { landmarkId: capturePlaceId.value })
  event.target.value = ""
}

function openBook() {
  if (openingBook.value) return
  selectedLandmarkId.value = ""
  openingBook.value = true

  window.setTimeout(() => {
    changeScreen("book")
  }, 940)

  window.setTimeout(() => {
    openingBook.value = false
  }, 1420)
}
</script>

<template>
  <main class="app-shell">
    <section class="phone" aria-label="拍迹移动端 Web App">
      <div class="screens">
        <HomePage
          :active="screen === 'home'"
          :book-title="bookTitle"
          :card-count="totalCardCount"
          @create-book="changeScreen('create')"
          @open-book="openBook"
          @quick-capture="openCapturePanel"
        />
        <CreateBookPage
          :active="screen === 'create'"
          v-model:title="bookTitle"
          @back="changeScreen('home')"
          @create-book="changeScreen('book'); showToast(`已创建《${bookTitle}》`)"
          @add-photos="addPhotos"
        />
        <BookDetailPage
          :active="screen === 'book'"
          :title="bookTitle"
          :landmarks="landmarks"
          :selected-id="selectedLandmarkId"
          @back="changeScreen('home')"
          @select-landmark="selectedLandmarkId = $event"
          @back-map="selectedLandmarkId = ''"
          @add-photos="addPhotos"
          @share="openSharePanel"
        />
        <CommunityPage
          :active="screen === 'community'"
        />
      </div>
      <BottomTabBar :active-screen="activeScreen" @change="changeScreen" />

      <div v-if="capturePanelOpen" class="capture-panel" @pointerdown.stop>
        <div class="capture-panel-head">
          <strong>拍照加入旅行书</strong>
          <button type="button" @click="capturePanelOpen = false">取消</button>
        </div>
        <label>
          <span>选择书</span>
          <select :value="bookTitle" disabled>
            <option>{{ bookTitle }}</option>
          </select>
        </label>
        <label>
          <span>选择地点</span>
          <select v-model="capturePlaceId">
            <option v-for="item in landmarks" :key="item.id" :value="item.id">
              {{ item.name }}
            </option>
          </select>
          <small>已根据当前定位优先推荐附近地点</small>
        </label>
        <div class="capture-panel-actions">
          <button class="cta stamp" type="button" @click="triggerPanelCamera">拍照新增</button>
          <button class="cta paper-cta" type="button" @click="triggerPanelAlbum">相册导入</button>
        </div>
      </div>

      <div v-if="cardGeneration.active" class="generation-panel" role="status" aria-live="polite">
        <div class="generation-copy">
          <strong>{{ generationTitle }}</strong>
          <span>{{ generationSubtitle }}</span>
        </div>
        <div class="generation-track">
          <span :style="{ width: `${generationPercent}%` }" />
        </div>
      </div>

      <div v-if="sharePanelOpen" class="share-sheet" @click.self="sharePanelOpen = false">
        <section>
          <div class="share-sheet-head">
            <strong>{{ sharePayload?.type === "card" ? "分享这张卡片" : "下载这本书" }}</strong>
            <button type="button" @click="sharePanelOpen = false">关闭</button>
          </div>
          <div class="share-preview">
            <span v-if="shareImageLoading">正在生成 PNG 预览...</span>
            <img v-else-if="shareImageUrl" :src="shareImageUrl" alt="将要下载的分享图片预览" />
          </div>
          <p>{{ shareCopy }}</p>
          <div class="share-actions">
            <button type="button" :disabled="!shareImageUrl" @click="downloadShareImage">下载 PNG</button>
            <button type="button" @click="copyShareText">复制文案</button>
            <button type="button" @click="openPlatform('xiaohongshu')">小红书</button>
            <button type="button" @click="openPlatform('douyin')">抖音</button>
          </div>
        </section>
      </div>

      <div v-if="openingBook" class="book-open-transition" aria-hidden="true">
        <div class="transition-glow" />
        <div class="animated-book">
          <div class="book-spread">
            <div class="spread-page spread-left">
              <span class="page-line wide" />
              <span class="page-line" />
              <span class="page-dot" />
            </div>
            <div class="spread-page spread-right">
              <span class="mini-map" />
              <span class="page-line wide" />
              <span class="page-line" />
            </div>
            <div class="front-cover">
              <span class="transition-cover-image" />
              <span class="cover-photo" />
              <span class="cover-title">{{ bookTitle }}</span>
              <span class="cover-subtitle">旅行书</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="toast" :class="{ show: toast }" role="status" aria-live="polite">
      {{ toast }}
    </div>

    <input
      ref="panelCameraInput"
      class="visually-hidden"
      type="file"
      accept="image/*"
      capture="environment"
      @change="handlePanelFiles($event, 'camera')"
    />
    <input
      ref="panelAlbumInput"
      class="visually-hidden"
      type="file"
      accept="image/*"
      multiple
      @change="handlePanelFiles($event, 'album')"
    />
  </main>
</template>
