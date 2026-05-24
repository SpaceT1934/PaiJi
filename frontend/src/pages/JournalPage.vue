<script setup>
import { computed, ref, watch } from "vue"
import { Camera, ChevronLeft, Images, MapPin, Maximize2, Minus, Plus, Route, Share2 } from "lucide-vue-next"

const props = defineProps({
  active: Boolean,
  title: {
    type: String,
    required: true
  },
  landmarks: {
    type: Array,
    required: true
  },
  selectedId: {
    type: String,
    default: ""
  }
})

const emit = defineEmits(["back", "back-map", "select-landmark", "add-photos", "share"])
const cameraInput = ref(null)
const albumInput = ref(null)
const zoom = ref(1)
const pan = ref({ x: 0, y: 0 })
const dragState = ref(null)
const openingId = ref("")
const canvasZoom = ref(0.62)
const canvasPan = ref({ x: -142, y: -172 })
const canvasDragState = ref(null)
const canvasPointers = new Map()
const canvasPinchState = ref(null)
const activePointers = new Map()
const pinchState = ref(null)
const cardToast = ref("")
const selectedCanvasCard = ref(null)
const activeTag = ref(null)
const cardSwitching = ref(false)
const promptBouncing = ref(false)
const cameraGuideVisible = ref(false)
let cardToastTimer

const selectedLandmark = computed(() => props.landmarks.find((item) => item.id === props.selectedId))
watch(
  () => [props.selectedId, selectedLandmark.value?.cards?.length || 0],
  ([id, count], [oldId, oldCount]) => {
    if (id && id === oldId && count > oldCount) {
      selectedCanvasCard.value = null
      activeTag.value = null
      cameraGuideVisible.value = false
      resetCanvas()
      cardToast.value = "新卡片已贴进这页手账"
      window.clearTimeout(cardToastTimer)
      cardToastTimer = window.setTimeout(() => {
        cardToast.value = ""
      }, 1800)
    }
  }
)
const headerTitle = computed(() => {
  if (selectedCanvasCard.value) return selectedCanvasCard.value.title
  if (selectedLandmark.value) return selectedLandmark.value.name
  return props.title
})
const headerSubtitle = computed(() => {
  if (selectedCanvasCard.value) return selectedCanvasCard.value.subtitle
  if (selectedLandmark.value) return `${selectedLandmark.value.lat.toFixed(4)}, ${selectedLandmark.value.lng.toFixed(4)}`
  return `${props.landmarks.length} 个 GPS 地标 · 点击进入卡片`
})
const mapTransform = computed(() => ({
  transform: `translate(${pan.value.x}px, ${pan.value.y}px) scale(${zoom.value})`
}))
const canvasTransform = computed(() => ({
  transform: `translate(${canvasPan.value.x}px, ${canvasPan.value.y}px) scale(${canvasZoom.value})`
}))
const currentCard = computed(() => selectedCanvasCard.value || {})
const currentCardBody = computed(() => currentCard.value.body || currentCard.value.text || "")
const currentCardPrompt = computed(() => currentCard.value.nextPrompt || currentCard.value.next_prompt || "再拍一张相关细节")
const currentPhotoStyle = computed(() => ({
  backgroundImage: `url(${selectedCanvasCard.value?.image || ""})`,
  backgroundSize: selectedCanvasCard.value?.id === "fuzimiao-food" ? "contain" : "cover",
  backgroundPosition: "center"
}))
const currentCardTime = computed(() => {
  if (!currentCard.value.capturedAt) return "刚刚生成"
  return new Date(currentCard.value.capturedAt).toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  })
})
const currentHotspots = computed(() => (Array.isArray(currentCard.value.hotspots) ? currentCard.value.hotspots : []))
const shareTarget = computed(() => {
  if (selectedCanvasCard.value) {
    return {
      type: "card",
      title: selectedCanvasCard.value.title,
      subtitle: selectedCanvasCard.value.subtitle || selectedCanvasCard.value.category || "旅行故事卡",
      body: currentCardBody.value,
      image: selectedCanvasCard.value.image || "",
      tags: selectedCanvasCard.value.tags || [],
      watermark: "拍迹 TripNote",
      filename: "tripnote-card.png"
    }
  }

  if (selectedLandmark.value) {
    return {
      type: "book",
      title: `${selectedLandmark.value.name}手账地图`,
      subtitle: props.title,
      body: selectedLandmark.value.text,
      image: "/tripnote/assets/nanjing_map.png",
      tags: [
        { label: "📍 地图" },
        { label: "📖 旅行书" },
        { label: "✍️ 手账" }
      ],
      watermark: "拍迹 TripNote",
      filename: "tripnote-map.png"
    }
  }

  return {
    type: "book",
    title: `${props.title}地图`,
    subtitle: `${props.landmarks.length} 个 GPS 地标`,
    body: "把一次旅行的照片整理成一本可以翻阅的旅行手账。",
    image: "/tripnote/assets/nanjing_map.png",
    tags: [
      { label: "📍 地图" },
      { label: "📖 旅行书" },
      { label: "✍️ 手账" }
    ],
    watermark: "拍迹 TripNote",
    filename: "tripnote-map.png"
  }
})

function clampPan(nextPan, nextZoom = zoom.value) {
  const max = (nextZoom - 1) * 170
  if (max <= 0) return { x: 0, y: 0 }
  return {
    x: Math.min(max, Math.max(-max, nextPan.x)),
    y: Math.min(max, Math.max(-max, nextPan.y))
  }
}

function setZoom(nextZoom) {
  zoom.value = Math.min(2.4, Math.max(1, Number(nextZoom.toFixed(2))))
  pan.value = clampPan(pan.value, zoom.value)
}

function clampCanvasPan(nextPan, nextZoom = canvasZoom.value) {
  const maxX = 780 * nextZoom
  const maxY = 1000 * nextZoom
  return {
    x: Math.min(160, Math.max(-maxX, nextPan.x)),
    y: Math.min(120, Math.max(-maxY, nextPan.y))
  }
}

function setCanvasZoom(nextZoom) {
  canvasZoom.value = Math.min(2.4, Math.max(0.42, Number(nextZoom.toFixed(2))))
  canvasPan.value = clampCanvasPan(canvasPan.value, canvasZoom.value)
}

function zoomCanvasIn() {
  setCanvasZoom(canvasZoom.value + 0.18)
}

function zoomCanvasOut() {
  setCanvasZoom(canvasZoom.value - 0.18)
}

function resetCanvas() {
  canvasZoom.value = 0.62
  canvasPan.value = { x: -142, y: -172 }
}

function cardStyle(index) {
  const columns = 2
  const col = index % columns
  const row = Math.floor(index / columns)
  const baseX = col === 0 ? 110 : 690
  const baseY = 690 + row * 220
  const jitterX = col === 0 ? (row % 2) * 18 : -(row % 2) * 16
  const rotateList = [-10, 8, -6, 9]
  const rotate = rotateList[index % rotateList.length]
  return {
    left: `${baseX + jitterX}px`,
    top: `${baseY}px`,
    transform: `rotate(${rotate}deg)`,
    "--rotate": `${rotate}deg`
  }
}

function distanceBetween(points) {
  const [a, b] = points
  return Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY)
}

function zoomIn() {
  setZoom(zoom.value + 0.25)
}

function zoomOut() {
  setZoom(zoom.value - 0.25)
}

function resetMap() {
  zoom.value = 1
  pan.value = { x: 0, y: 0 }
}

function openLandmark(landmark) {
  openingId.value = landmark.id
  zoom.value = 2.05
  pan.value = clampPan({
    x: (50 - landmark.x) * 6,
    y: (50 - landmark.y) * 6
  }, zoom.value)

  window.setTimeout(() => {
    emit("select-landmark", landmark.id)
    openingId.value = ""
    resetMap()
  }, 980)
}

function startDrag(event) {
  activePointers.set(event.pointerId, { clientX: event.clientX, clientY: event.clientY })
  if (activePointers.size === 2) {
    const points = Array.from(activePointers.values())
    pinchState.value = {
      startDistance: distanceBetween(points),
      startZoom: zoom.value,
      startPan: { ...pan.value }
    }
    dragState.value = null
    event.currentTarget.setPointerCapture?.(event.pointerId)
    return
  }

  if (zoom.value <= 1) return
  dragState.value = {
    pointerId: event.pointerId,
    startX: event.clientX,
    startY: event.clientY,
    panX: pan.value.x,
    panY: pan.value.y
  }
  event.currentTarget.setPointerCapture?.(event.pointerId)
}

function moveDrag(event) {
  if (activePointers.has(event.pointerId)) {
    activePointers.set(event.pointerId, { clientX: event.clientX, clientY: event.clientY })
  }

  if (pinchState.value && activePointers.size >= 2) {
    const points = Array.from(activePointers.values()).slice(0, 2)
    const ratio = distanceBetween(points) / Math.max(1, pinchState.value.startDistance)
    const nextZoom = Math.min(2.4, Math.max(1, pinchState.value.startZoom * ratio))
    zoom.value = Number(nextZoom.toFixed(2))
    pan.value = clampPan(pinchState.value.startPan, zoom.value)
    return
  }

  if (!dragState.value) return
  const nextPan = {
    x: dragState.value.panX + event.clientX - dragState.value.startX,
    y: dragState.value.panY + event.clientY - dragState.value.startY
  }
  pan.value = clampPan(nextPan)
}

function endDrag(event) {
  if (event?.pointerId) activePointers.delete(event.pointerId)
  if (activePointers.size < 2) pinchState.value = null
  dragState.value = null
}

function startCanvasDrag(event) {
  canvasPointers.set(event.pointerId, { clientX: event.clientX, clientY: event.clientY })
  if (canvasPointers.size === 2) {
    const points = Array.from(canvasPointers.values())
    canvasPinchState.value = {
      startDistance: distanceBetween(points),
      startZoom: canvasZoom.value,
      startPan: { ...canvasPan.value }
    }
    canvasDragState.value = null
    event.currentTarget.setPointerCapture?.(event.pointerId)
    return
  }

  canvasDragState.value = {
    pointerId: event.pointerId,
    startX: event.clientX,
    startY: event.clientY,
    panX: canvasPan.value.x,
    panY: canvasPan.value.y
  }
  event.currentTarget.setPointerCapture?.(event.pointerId)
}

function moveCanvasDrag(event) {
  if (canvasPointers.has(event.pointerId)) {
    canvasPointers.set(event.pointerId, { clientX: event.clientX, clientY: event.clientY })
  }

  if (canvasPinchState.value && canvasPointers.size >= 2) {
    const points = Array.from(canvasPointers.values()).slice(0, 2)
    const ratio = distanceBetween(points) / Math.max(1, canvasPinchState.value.startDistance)
    const nextZoom = Math.min(2.4, Math.max(0.42, canvasPinchState.value.startZoom * ratio))
    canvasZoom.value = Number(nextZoom.toFixed(2))
    canvasPan.value = clampCanvasPan(canvasPinchState.value.startPan, canvasZoom.value)
    return
  }

  if (!canvasDragState.value) return
  canvasPan.value = clampCanvasPan({
    x: canvasDragState.value.panX + event.clientX - canvasDragState.value.startX,
    y: canvasDragState.value.panY + event.clientY - canvasDragState.value.startY
  })
}

function endCanvasDrag(event) {
  if (event?.pointerId) canvasPointers.delete(event.pointerId)
  if (canvasPointers.size < 2) canvasPinchState.value = null
  canvasDragState.value = null
}

function openCamera() {
  cameraInput.value?.click()
}

function openAlbum() {
  albumInput.value?.click()
}

function handleFiles(event, source) {
  emit("add-photos", event.target.files, source, { landmarkId: selectedLandmark.value?.id || "" })
  event.target.value = ""
}

function showCardPlaceholder(label) {
  cardToast.value = `${label} 卡片还没生成`
  window.clearTimeout(cardToastTimer)
  cardToastTimer = window.setTimeout(() => {
    cardToast.value = ""
  }, 1400)
}

function openCanvasCard(card) {
  selectedCanvasCard.value = {
    ...card,
    tags: normalizeTags(card.tags, card.category),
    hotspots: Array.isArray(card.hotspots) ? card.hotspots : []
  }
  activeTag.value = null
}

function normalizeTags(tags, category = "旅行") {
  const fallback = [
    { label: `✨ ${category || "旅行"}`, popupText: "这是照片里最适合继续展开的旅行线索。" },
    { label: "📍 此刻", popupText: "这一刻被贴进了当前位置的旅行手账里。" },
    { label: "🖼️ 画面", popupText: "照片里的颜色、主体和氛围会一起变成卡片记忆。" }
  ]
  if (!Array.isArray(tags) || !tags.length) return fallback
  return tags.slice(0, 3).map((tag, index) => {
    if (typeof tag === "object" && tag) {
      return {
        label: tag.label || fallback[index]?.label || "✨ 旅行",
        popupText: tag.popupText || tag.text || fallback[index]?.popupText || "这是一条值得继续展开的小线索。"
      }
    }
    return {
      label: String(tag),
      popupText: `${tag} 是这张照片里值得点开看的旅行线索。`
    }
  })
}

function openTag(tag) {
  activeTag.value = tag
}

function findCardById(id) {
  return selectedLandmark.value?.cards?.find((card) => card.id === id)
}

function openHotspot(hotspot) {
  if (hotspot.nextCardId) {
    const nextCard = findCardById(hotspot.nextCardId)
    if (nextCard) {
      cardSwitching.value = true
      window.setTimeout(() => {
        openCanvasCard(nextCard)
        window.requestAnimationFrame(() => {
          cardSwitching.value = false
        })
      }, 170)
      return
    }
  }
  activeTag.value = {
    label: hotspot.label || "继续探索",
    popupText: hotspot.popupText || "这是照片里值得继续展开的小线索。"
  }
}

function closeTag() {
  activeTag.value = null
}

function openPromptCamera() {
  promptBouncing.value = true
  cameraGuideVisible.value = true
  window.setTimeout(() => {
    promptBouncing.value = false
  }, 520)
  window.setTimeout(() => {
    openCamera()
  }, 260)
  window.setTimeout(() => {
    cameraGuideVisible.value = false
  }, 1800)
}

function goBack() {
  if (selectedCanvasCard.value) {
    selectedCanvasCard.value = null
    activeTag.value = null
    return
  }
  if (selectedLandmark.value) {
    emit("back-map")
    return
  }
  emit("back")
}
</script>

<template>
  <section class="screen book-screen" :class="{ active }" aria-label="南京周末漫游地图">
    <header class="page-head detail-head">
      <button class="round-button" aria-label="返回" @click="goBack">
        <ChevronLeft :size="18" />
      </button>
      <div>
        <h2>{{ headerTitle }}</h2>
        <p>{{ headerSubtitle }}</p>
      </div>
        <button class="round-button share-button" aria-label="分享" @click="emit('share', shareTarget)">
          <Share2 :size="17" />
        </button>
        <button class="round-button add-card-button" aria-label="拍照新增卡片" @click="openCamera">
          <Camera :size="17" />
        </button>
      </header>

    <section
      v-if="!selectedLandmark"
      class="map-page"
      :class="{ dragging: dragState, opening: openingId }"
      aria-label="旅行书地图"
      @pointerdown="startDrag"
      @pointermove="moveDrag"
      @pointerup="endDrag"
      @pointercancel="endDrag"
      @pointerleave="endDrag"
    >
      <div class="map-transform" :style="mapTransform">
        <img :src="'/tripnote/assets/nanjing_map.png'" alt="南京手账地图底板" draggable="false" />
        <svg class="route-layer" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <polyline
            :points="landmarks.map((item) => `${item.x},${item.y}`).join(' ')"
            fill="none"
            stroke="rgba(185, 78, 59, 0.58)"
            stroke-width="1.7"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-dasharray="4 4"
          />
        </svg>

        <button
          v-for="landmark in landmarks"
          :key="landmark.id"
          class="landmark-pin"
          :style="{ left: `${landmark.x}%`, top: `${landmark.y}%` }"
          type="button"
          @click.stop="openLandmark(landmark)"
        >
          <MapPin :size="17" />
          <span>{{ landmark.name }}</span>
        </button>
      </div>

      <div class="map-controls" @pointerdown.stop>
        <button type="button" aria-label="放大地图" @click="zoomIn">
          <Plus :size="16" />
        </button>
        <button type="button" aria-label="缩小地图" @click="zoomOut">
          <Minus :size="16" />
        </button>
        <button type="button" aria-label="重置地图" @click="resetMap">
          <Maximize2 :size="15" />
        </button>
      </div>

      <div class="zoom-badge">{{ Math.round(zoom * 100) }}%</div>

      <div class="map-caption">
        <Route :size="16" />
        已根据定位生成旅行路线
      </div>
    </section>

    <article
      v-else-if="!selectedCanvasCard"
      class="journal-spread infinite-board"
      :class="{ dragging: canvasDragState }"
      @pointerdown="startCanvasDrag"
      @pointermove="moveCanvasDrag"
      @pointerup="endCanvasDrag"
      @pointercancel="endCanvasDrag"
      @pointerleave="endCanvasDrag"
    >
      <div class="journal-canvas-large" :style="canvasTransform">
        <div class="canvas-bg" />
        <div class="flapbook-fold" />

        <div class="canvas-head">
          <MapPin :size="18" />
          <span>{{ selectedLandmark.name }}</span>
        </div>

        <div class="canvas-title">
          <h3>{{ selectedLandmark.name }}故事线</h3>
          <p>点一张线索卡，再点照片里的发光入口，就能翻到下一段旅行故事。</p>
        </div>

        <svg v-if="selectedLandmark.cards.length > 1" class="story-route" viewBox="0 0 1000 1260" aria-hidden="true">
          <path
            class="story-route-shadow"
            d="M170 790 C 330 650, 610 720, 830 640 S 900 860, 790 1045 S 420 1120, 165 1095"
          />
          <path
            class="story-route-line"
            d="M170 790 C 330 650, 610 720, 830 640 S 900 860, 790 1045 S 420 1120, 165 1095"
          />
          <path class="story-arrow" d="M812 630 l42 8 l-30 30" />
          <path class="story-arrow second" d="M776 1018 l32 34 l-44 10" />
          <text x="350" y="666">猫的视线</text>
          <text x="804" y="850">灯光</text>
          <text x="398" y="1136">城市纹理</text>
        </svg>

        <button
          class="canvas-sticker sticker-gps"
          type="button"
          @click.stop="openCanvasCard({
            title: 'GPS 位置',
            subtitle: '定位卡片',
            body: `${selectedLandmark.name} 的真实坐标：${selectedLandmark.lat.toFixed(6)}, ${selectedLandmark.lng.toFixed(6)}。这本书会把同一地点的照片收进同一段手账里。`,
            tone: '#d9e3e1'
          })"
        >
          <MapPin :size="19" />
          <strong>GPS 位置</strong>
          <small>{{ selectedLandmark.lat.toFixed(4) }}, {{ selectedLandmark.lng.toFixed(4) }}</small>
        </button>

        <button
          class="canvas-sticker sticker-tag"
          type="button"
          @click.stop="openCanvasCard({
            title: '探索标签',
            subtitle: '标签卡片',
            body: '这里会展示照片里的可点击标签，比如美食、文物、风景、小动物。点击标签后可以展开这一页背后的趣味故事。',
            tone: '#f0cdbf'
          })"
        >
          <span class="tag-mark">#</span>
          <strong>探索标签</strong>
          <small>美食 / 文物 / 风景</small>
        </button>

        <button
          v-for="(card, index) in selectedLandmark.cards"
          :key="card.id"
          class="canvas-sticker user-photo"
          :style="cardStyle(index)"
          type="button"
          @click.stop="openCanvasCard({
            id: card.id,
            title: card.title,
            subtitle: card.category || '旅行故事卡',
            image: card.image,
            body: card.text,
            tone: card.tone,
            tags: card.tags,
            hotspots: card.hotspots,
            category: card.category,
            nextPrompt: card.nextPrompt,
            capturedAt: card.capturedAt
          })"
        >
          <span class="story-step">{{ String(index + 1).padStart(2, "0") }}</span>
          <span class="sticker-image" :style="{ backgroundImage: `url(${card.image})` }" />
          <strong>{{ card.title }}</strong>
          <small>{{ card.category || "旅行故事卡" }}</small>
        </button>

        <div class="canvas-toast" :class="{ show: cardToast }">{{ cardToast }}</div>
      </div>

      <div class="canvas-controls" @pointerdown.stop>
        <button type="button" aria-label="放大手账画布" @click="zoomCanvasIn">
          <Plus :size="16" />
        </button>
        <button type="button" aria-label="缩小手账画布" @click="zoomCanvasOut">
          <Minus :size="16" />
        </button>
        <button type="button" aria-label="重置手账画布" @click="resetCanvas">
          <Maximize2 :size="15" />
        </button>
      </div>

      <div class="zoom-badge canvas-zoom">{{ Math.round(canvasZoom * 100) }}%</div>
    </article>

    <article v-else class="card-detail-page">
      <div class="ai-photo-card" :class="{ switching: cardSwitching }">
        <div v-if="selectedCanvasCard.image" class="ai-card-photo" :style="currentPhotoStyle">
          <button
            v-for="hotspot in currentHotspots"
            :key="hotspot.label"
            class="photo-hotspot"
            type="button"
            :style="{ left: `${hotspot.x}%`, top: `${hotspot.y}%` }"
            @click.stop="openHotspot(hotspot)"
          >
            <span />
            {{ hotspot.label }}
          </button>
        </div>
        <div class="ai-card-content">
          <span class="ai-card-kicker">{{ selectedCanvasCard.subtitle || selectedCanvasCard.category || "旅行故事卡" }}</span>
          <h3>{{ selectedCanvasCard.title }}</h3>
          <p class="ai-card-body">{{ currentCardBody }}</p>

          <div v-if="currentHotspots.length" class="shoot-chain-tip">
            点照片里的拍摄提示，继续翻到下一张卡片
          </div>

          <div class="ai-tag-row" aria-label="照片标签">
            <button
              v-for="tag in selectedCanvasCard.tags"
              :key="tag.label"
              type="button"
              @click="openTag(tag)"
            >
              {{ tag.label }}
            </button>
          </div>

          <button class="next-prompt" type="button" @click="openPromptCamera">
            <span>{{ currentCardPrompt }} →</span>
            <Camera :class="{ bounce: promptBouncing }" :size="18" />
          </button>

          <div class="ai-card-foot">
            <small>{{ currentCardTime }}</small>
            <small>拍迹 TripNote</small>
          </div>
        </div>
      </div>

      <div v-if="cameraGuideVisible" class="camera-guide">
        <span>将主体对准框内拍照</span>
        <div />
      </div>

      <div v-if="activeTag" class="tag-sheet" @click.self="closeTag">
        <section>
          <strong>{{ activeTag.label }}</strong>
          <p>{{ activeTag.popupText }}</p>
          <button type="button" @click="closeTag">知道了</button>
        </section>
      </div>
    </article>

    <div v-if="!selectedCanvasCard" class="add-actions">
      <button class="cta stamp" @click="openCamera">
        <Camera :size="18" />
        拍照新增
      </button>
      <button class="cta paper-cta" @click="openAlbum">
        <Images :size="18" />
        相册导入
      </button>
    </div>

    <input
      ref="cameraInput"
      class="visually-hidden"
      type="file"
      accept="image/*"
      capture="environment"
      @change="handleFiles($event, 'camera')"
    />
    <input
      ref="albumInput"
      class="visually-hidden"
      type="file"
      accept="image/*"
      multiple
      @change="handleFiles($event, 'album')"
    />
  </section>
</template>
