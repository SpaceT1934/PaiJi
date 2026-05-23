<script setup>
import { Menu } from "lucide-vue-next"

defineProps({
  eyebrow: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  }
})

const emit = defineEmits(["menu"])
</script>

<template>
  <header class="app-header">
    <div>
      <p>{{ eyebrow }}</p>
      <h2>{{ title }}</h2>
    </div>
    <button class="round-button" aria-label="菜单" @click="emit('menu')">
      <Menu :size="19" />
    </button>
  </header>
</template>
