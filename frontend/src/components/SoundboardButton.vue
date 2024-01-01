<script setup>
import TrackRepository from '@/assets/TrackRepository'
import { computed } from 'vue'

const props = defineProps({
  trackId: String
})

const eventEmit = defineEmits(['rightClick'])

function rightClickAction (event) {
  event.preventDefault()
  eventEmit('rightClick', props.trackId, event.pageX, event.pageY)
}

const track = TrackRepository.getTrack(props.trackId)
const active = computed(() => track.active)

function play () {
  fetch(`/play/${props.trackId}/0.0`)
}
</script>

<template>
  <button @contextmenu="rightClickAction" @click="play"
    class="relative transition-colors duration-150 ease-in-out border border-gray-500 my-1 md:border-0 w-screen h-10 md:w-40 md:h-32 md:rounded-xl md:m-2 md:p-4"
    :class="[active ? 'bg-red-300' : 'bg-gray-300']">
    <p>{{ track.name }}</p>
  </button>
</template>
