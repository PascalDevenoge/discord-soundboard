<script setup>
const props = defineProps({
  title: String,
  okAction: Function
})

const eventEmit = defineEmits(['close'])

function okHandler () {
  props.okAction()
  eventEmit('close')
}
</script>

<template>
  <div @click="eventEmit('click')" class="fixed top-0 left-0 w-screen h-screen bg-gray-400/50">
    <div @click.stop class="fixed bg-white top-1/4 left-2/4 -translate-x-2/4 rounded-xl border border-gray-400">
      <div
        class="grid gap-y-1 divide-y divide-gray-400 items-stretch justify-stretch content-stretch min-w-96 min-h-12 m-6">
        <div class="min-h-8">
          <p class="font-bold text-lg align-middle">{{ props.title }}</p>
        </div>
        <div>
          <slot/>
        </div>
        <div class="min-h-8">
          <button class="float-right text-white font-semibold rounded-md h-8 bg-blue-600 hover:bg-blue-500 min-w-12 mt-3 mx-2 px-2" @click="okHandler">Ok</button>
          <button class="float-right text-white font-semibold rounded-md h-8 bg-blue-600 hover:bg-blue-500 min-w-12 mt-3 mx-2 px-2" @click="eventEmit('close')">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.grid {
  grid-template-rows: auto 1fr auto;
}
</style>
