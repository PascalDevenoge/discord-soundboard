<script setup>
import TrackRepository from '@/assets/TrackRepository'
import { computed } from 'vue'

const props = defineProps({
  trackId: String,
  rightClickAction: Function
})

const track = TrackRepository.getTrack(props.trackId)
const active = computed(() => track.active)

function play () {
  fetch(`/play/${props.trackId}/0.0`)
}

function rightClickEventHandler (event) {
  event.preventDefault()
  props.rightClickAction(props.trackId)
}
</script>

<template>
  <button @contextmenu="rightClickEventHandler" @click="play"
    class="transition-colors duration-200 ease-in-out border border-gray-500 my-1 md:border-0 w-screen h-10 md:w-40 md:h-32 md:rounded-xl md:m-2 md:p-4"
    :class="[active ? 'bg-red-300' : 'bg-gray-300']">{{ track.name }}</button></template>
