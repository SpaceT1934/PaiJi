<script setup>
import { computed, ref } from "vue"
import BottomTabBar from "./components/BottomTabBar.vue"
import CreateBookPage from "./pages/GeneratePage.vue"
import BookDetailPage from "./pages/JournalPage.vue"
import HomePage from "./pages/HomePage.vue"

const screen = ref("home")
const toast = ref("")
const bookTitle = ref("南京周末漫游")
const generatedCards = ref([])
let toastTimer

const activeScreen = computed(() => (screen.value === "community" || screen.value === "profile" ? "home" : screen.value))

function showToast(message) {
  toast.value = message
  window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    toast.value = ""
  }, 1800)
}

function changeScreen(target) {
  if (target === "community") {
    showToast("社区暂未开放")
    return
  }

  if (target === "profile") {
    showToast("我的暂未开放")
    return
  }

  screen.value = target
}

function createCard(file, index) {
  const url = URL.createObjectURL(file)
  const titles = ["新拍到的南京瞬间", "街角新页", "旅行书的新一页", "刚刚加入的画面"]
  const colors = ["#dfe9d7", "#f0d8c7", "#e6d8b8", "#d9e3e1"]
  return {
    id: `${Date.now()}-${file.name}-${index}`,
    url,
    title: titles[(generatedCards.value.length + index) % titles.length],
    color: colors[(generatedCards.value.length + index) % colors.length],
    text: "AI 已读取这张照片的颜色和主体，正在把它整理成当前旅行书里的新卡片。"
  }
}

function addPhotos(files, source = "camera") {
  const list = Array.from(files || []).filter((file) => file.type.startsWith("image/"))
  if (!list.length) {
    showToast("还没有选择照片")
    return
  }

  generatedCards.value = [...list.map(createCard), ...generatedCards.value]
  screen.value = "book"
  showToast(source === "camera" ? "已新增拍照卡片" : `已从相册导入 ${list.length} 张`)
}
</script>

<template>
  <main class="app-shell">
    <section class="phone" aria-label="拍迹移动端 Web App">
      <div class="screens">
        <HomePage
          :active="screen === 'home'"
          :book-title="bookTitle"
          :card-count="3 + generatedCards.length"
          @create-book="changeScreen('create')"
          @open-book="changeScreen('book')"
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
          :cards="generatedCards"
          @back="changeScreen('home')"
          @add-photos="addPhotos"
          @share="showToast('分享链接将在后端接入后生成')"
        />
      </div>
      <BottomTabBar :active-screen="activeScreen" @change="changeScreen" />
    </section>

    <div class="toast" :class="{ show: toast }" role="status" aria-live="polite">
      {{ toast }}
    </div>
  </main>
</template>
