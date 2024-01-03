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
  fetch('/play?' + new URLSearchParams({
    id: props.trackId,
    volume: 0.0
  }))
}
</script>

<template>
  <button @contextmenu="rightClickAction" @click="play"
    class="relative overflow-hidden transition-colors transition-transform duration-150 ease-in-out md:hover:scale-105 border border-gray-500 my-1 md:border-0 w-screen h-10 md:w-32 md:h-24 md:rounded-xl md:m-2 md:p-4"
    :class="[active ? 'bg-red-300' : 'bg-gray-300']">
    <p class="text-sm">{{ track.name }}</p>
  </button>
</template>
