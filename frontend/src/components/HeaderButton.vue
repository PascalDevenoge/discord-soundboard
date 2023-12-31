<script setup>
const props = defineProps({
  highlighted: {
    default: false,
    type: Boolean
  }
})

const eventEmit = defineEmits(['click'])
</script>

<template>
  <button @click="eventEmit('click')"
    class="w-screen md:w-64 md:mx-8 p-3 md:rounded-xl font-sans font-bold text-xl text-white"
    :class="[props.highlighted ? 'bg-red-600' : 'bg-blue-600', props.highlighted ? 'hover:bg-red-500' : 'hover:bg-blue-500']">
    <slot />
  </button>
</template>
