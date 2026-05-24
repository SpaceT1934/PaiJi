<script setup>
import { BookOpen, Camera, ChevronRight, Images, MapPin } from "lucide-vue-next"

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

const emit = defineEmits(["create-book", "open-book", "quick-capture"])

const assetUrl = (name) => `${import.meta.env.BASE_URL}assets/${name}`
</script>

<template>
  <section class="screen home-screen home-desk" :class="{ active }" aria-label="书架首页">
    <div class="desk-decoration tape-one" />
    <div class="desk-decoration tape-two" />

    <header class="home-hero-head">
      <div>
        <h1>拍迹</h1>
        <p>
          <span>把随手拍的照片，</span>
          <span>生成一本会说话的旅行书</span>
        </p>
      </div>
      <button class="floating-book-button" type="button" aria-label="打开书架" @click="emit('open-book')">
        <BookOpen :size="23" />
      </button>
    </header>

    <section class="open-travel-book" aria-label="南京旅行书预览">
      <div class="route-dash" />
      <div class="map-pocket">
        <MapPin :size="21" />
      </div>
      <button class="open-book-pages" type="button" @click="emit('open-book')">
        <div class="book-ring" />
        <article class="book-page left-page">
          <span class="paperclip" />
          <MapPin class="tiny-pin" :size="18" />
          <h2>{{ bookTitle }}</h2>
          <div class="travel-tags">
            <span>夫子庙</span>
            <span>秦淮河</span>
            <span>夜游</span>
          </div>
          <p>这本旅行书已经写好开头，点击继续完善你的故事吧</p>
          <div class="story-flow">
            <Camera :size="18" />
            <i />
            <BookOpen :size="18" />
          </div>
        </article>

        <article class="book-page right-page">
          <div class="polaroid main-polaroid">
            <img :src="assetUrl('fuzimiao-lantern-crowd.jpg')" alt="夫子庙夜景照片" />
            <strong>夫子庙的夜景</strong>
            <span class="heart-mark">♡</span>
          </div>
          <div class="polaroid small-polaroid">
            <img :src="assetUrl('fuzimiao-night-snack.jpg')" alt="南京小吃照片" />
          </div>
          <span class="page-curl" />
        </article>
      </button>
    </section>

    <button class="cta home-create-button" @click="emit('quick-capture')">
      <Camera :size="20" />
      点击开始随手拍照
    </button>

    <section class="my-books-panel" aria-label="我的旅行书">
      <header>
        <strong><BookOpen :size="16" /> 我的书架</strong>
        <button type="button" @click="emit('open-book')">查看全部 <ChevronRight :size="15" /></button>
      </header>
      <div class="mini-book-row">
        <button class="mini-book-card" type="button" @click="emit('open-book')">
          <span class="mini-book-rings" />
          <span class="mini-cover-photo">
            <img :src="assetUrl('fuzimiao-lantern-crowd.jpg')" alt="南京旅行书封面" />
          </span>
          <strong>{{ bookTitle }}</strong>
        </button>
        <article class="mini-book-card">
          <span class="mini-book-rings" />
          <span class="mini-cover-photo">
            <img :src="assetUrl('fuzimiao-cat-guide.jpg')" alt="苏州旅行书封面" />
          </span>
          <strong>苏州春日慢游</strong>
        </article>
      </div>
    </section>
  </section>
</template>
