<script setup>
import { ref } from "vue"
import { Camera, ChevronLeft, Images, Landmark } from "lucide-vue-next"

const props = defineProps({
  active: Boolean,
  title: {
    type: String,
    required: true
  }
})

const emit = defineEmits(["back", "create-book", "add-photos", "update:title"])
const cameraInput = ref(null)
const albumInput = ref(null)

const steps = [
  ["1", "创建书壳", "保存书名、封面和目的地"],
  ["2", "拍照新增", "每拍一张，AI 生成一张卡片"],
  ["3", "加入 Flapbook", "卡片自动进入当前这本书"]
]

function updateTitle(event) {
  emit("update:title", event.target.value)
}

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
  <section class="screen create-screen" :class="{ active }" aria-label="新建一本旅行书">
    <header class="page-head">
      <button class="round-button" aria-label="返回书架" @click="emit('back')">
        <ChevronLeft :size="18" />
      </button>
      <div>
        <h2>新建一本旅行书</h2>
        <p>先创建书，再不断拍照加页</p>
      </div>
    </header>

    <section class="create-card">
      <div class="cover-preview">
        <Landmark :size="54" />
        <div>
          <h3>{{ props.title || "未命名旅行书" }}</h3>
          <p>一本新书已准备好，从第一张照片开始。</p>
        </div>
      </div>

      <label class="field-block">
        <span>书名</span>
        <input
          :value="props.title"
          autocomplete="off"
          enterkeyhint="done"
          placeholder="给这本书起个名字"
          @input="updateTitle"
        />
      </label>

      <div class="field-block">
        <span>开始方式</span>
        <div class="segment-row">
          <button class="selected" type="button" @click="openCamera">
            <Camera :size="17" />
            拍照新增
          </button>
          <button type="button" @click="openAlbum">
            <Images :size="17" />
            相册导入
          </button>
        </div>
      </div>
    </section>

    <section class="logic-card">
      <h3>创建步骤</h3>
      <div v-for="[num, title, desc] in steps" :key="num" class="logic-step">
        <b>{{ num }}</b>
        <div>
          <strong>{{ title }}</strong>
          <span>{{ desc }}</span>
        </div>
      </div>
    </section>

    <button class="secondary-create" @click="emit('create-book')">只创建书壳</button>

    <button class="cta stamp" @click="openCamera">
      <Camera :size="18" />
      创建并拍第一张
    </button>

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
