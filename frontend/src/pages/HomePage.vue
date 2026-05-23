<script setup>
import { BookOpen, Camera, Images, MapPin, Sparkles, Waves } from "lucide-vue-next"

defineProps({
  active: Boolean,
  bookTitle: {
    type: String,
    required: true
  },
  cardCount: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(["create-book", "open-book"])
</script>

<template>
  <section class="screen home-screen" :class="{ active }" aria-label="书架首页">
    <header class="brand-head">
      <h1>拍迹</h1>
      <p>把随手拍的照片，生成一本会说话的旅行书</p>
    </header>

    <section class="book-universe" aria-label="旅行书书架">
      <div class="paper-grain" />
      <div class="brand-pill">
        <BookOpen :size="15" />
        <span>拍迹 · 旅行书生成器</span>
      </div>
      <BookOpen class="bookmark-mark" :size="30" />

      <button class="notebook notebook-nanjing" type="button" @click="emit('open-book')">
        <MapPin class="book-icon" :size="17" />
        <span class="photo-sticker nanjing-photo" />
        <span class="book-label teal-label">
          <strong>{{ bookTitle }}</strong>
          <small>{{ cardCount }} 张卡片</small>
        </span>
      </button>

      <article class="notebook notebook-xiamen" aria-label="厦门海风小记">
        <Waves class="book-icon" :size="17" />
        <span class="photo-sticker xiamen-photo" />
        <span class="book-label brown-label">
          <strong>厦门海风小记</strong>
          <small>待开启</small>
        </span>
      </article>

      <div class="shelf-caption">随机书架 · 每次旅行都能变成一本书</div>
    </section>

    <button class="cta stamp" @click="emit('create-book')">
      <Sparkles :size="18" />
      新建一本旅行书
    </button>

    <section class="quick-actions">
      <button type="button" @click="emit('open-book')">
        <Camera :size="18" />
        <strong>边拍边写</strong>
        <span>拍一张就加一页</span>
      </button>
      <button type="button" @click="emit('create-book')">
        <Images :size="18" />
        <strong>相册成书</strong>
        <span>批量整理旅行照片</span>
      </button>
    </section>
  </section>
</template>
