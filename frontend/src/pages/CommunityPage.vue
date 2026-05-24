<script setup>
import { BookOpen, MapPin, Users } from "lucide-vue-next"

defineProps({
  active: Boolean
})

const sharedBooks = [
  {
    city: "北京",
    x: 66,
    y: 34
  },
  {
    city: "南京",
    x: 61,
    y: 47
  },
  {
    city: "成都",
    x: 43,
    y: 54
  },
  {
    city: "广州",
    x: 57,
    y: 68
  }
]
</script>

<template>
  <section class="screen community-screen" :class="{ active }" aria-label="社区地图">
    <header class="community-head">
      <h2><Users :size="18" /> 社区旅行书</h2>
      <p>大家把自己的旅行书挂在地图上，故事会在这里相遇。</p>
    </header>

    <article class="community-map-card">
      <div class="community-map-layer" />
      <div
        v-for="item in sharedBooks"
        :key="item.city"
        class="community-pin"
        :style="{ left: `${item.x}%`, top: `${item.y}%` }"
      >
        <span class="pin-dot"><MapPin :size="12" /></span>
      </div>
    </article>

    <div class="community-footnote">
      <BookOpen :size="14" />
      你的旅行书也可以发布到社区地图
    </div>
  </section>
</template>
