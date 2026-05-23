<script setup>
import { computed, ref } from "vue"
import { Camera, ChevronLeft, Images, Landmark, Leaf, Share2, Soup, Sparkles } from "lucide-vue-next"

const props = defineProps({
  active: Boolean,
  title: {
    type: String,
    required: true
  },
  cards: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(["back", "add-photos", "share"])
const cameraInput = ref(null)
const albumInput = ref(null)
const latestCard = computed(() => props.cards[0])

function openCamera() {
  cameraInput.value?.click()
}

function openAlbum() {
  albumInput.value?.click()
}

function handleFiles(event, source) {
  emit("add-photos", event.target.files, source)
  event.target.value = ""
}
</script>

<template>
  <section class="screen book-screen" :class="{ active }" aria-label="南京周末漫游">
    <header class="page-head detail-head">
      <button class="round-button" aria-label="返回书架" @click="emit('back')">
        <ChevronLeft :size="18" />
      </button>
      <div>
        <h2>{{ title }}</h2>
        <p>{{ 3 + cards.length }} 张卡片 · 继续拍照扩充</p>
      </div>
      <button class="round-button share-button" aria-label="分享" @click="emit('share')">
        <Share2 :size="17" />
      </button>
    </header>

    <section class="collage-page" aria-label="AI 手账拼贴页">
      <div class="texture-lines" />
      <Sparkles class="float-mark spark" :size="38" />
      <Landmark class="float-mark landmark" :size="42" />

      <article class="memory-photo wall-photo">
        <span>
          <strong>明城墙</strong>
          <small>砖色把南京的历史翻开</small>
        </span>
      </article>

      <div class="bubble green-bubble">
        <Leaf :size="18" />
        <p>这张照片的主色是城砖红和树影绿，AI 会把它生成成“古城墙开场页”。</p>
      </div>

      <article class="memory-photo temple-photo">
        <span>
          <strong>鸡鸣寺一角</strong>
          <small>黄墙和屋檐很适合做章节封面</small>
        </span>
      </article>

      <div class="bubble gold-bubble">
        <Landmark :size="18" />
        <p>寺庙照片里黄色占比高，可以生成一条关于春日祈愿的卡片文案。</p>
      </div>

      <article class="memory-photo food-photo">
        <span>
          <strong>鸭血粉丝汤</strong>
          <small>把城市味道加进书里</small>
        </span>
      </article>

      <div class="bubble red-bubble">
        <Soup :size="18" />
        <p>拍完一碗热汤，AI 会把它变成这本书里的烟火气结尾。</p>
      </div>

      <article
        v-if="latestCard"
        class="memory-photo user-photo"
        :style="{ backgroundImage: `linear-gradient(180deg, transparent 38%, rgba(36, 90, 85, 0.88)), url(${latestCard.url})` }"
      >
        <span>
          <strong>{{ latestCard.title }}</strong>
          <small>刚刚新增到这本书</small>
        </span>
      </article>

      <div v-if="latestCard" class="bubble user-bubble" :style="{ background: latestCard.color }">
        <Sparkles :size="18" />
        <p>{{ latestCard.text }}</p>
      </div>
    </section>

    <div class="add-actions">
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
