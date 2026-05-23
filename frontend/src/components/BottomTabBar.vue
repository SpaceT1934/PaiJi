<script setup>
import { BookOpen, MessageCircle, Plus, User } from "lucide-vue-next"

defineProps({
  activeScreen: {
    type: String,
    required: true
  }
})

const emit = defineEmits(["change"])

const tabs = [
  { key: "home", label: "书架", icon: BookOpen },
  { key: "create", label: "创建", icon: Plus },
  { key: "community", label: "社区", icon: MessageCircle },
  { key: "profile", label: "我的", icon: User }
]
</script>

<template>
  <nav class="tabbar" aria-label="底部导航">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      class="tab"
      :class="{ active: activeScreen === tab.key }"
      @click="emit('change', tab.key)"
    >
      <component :is="tab.icon" :size="18" />
      {{ tab.label }}
    </button>
  </nav>
</template>
