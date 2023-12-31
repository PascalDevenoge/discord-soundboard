<script setup>
import TrackRepository from '@/assets/TrackRepository'

const props = defineProps({
  trackId: String,
  rightClickAction: Function
})

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
    class="border border-gray-500 my-1 md:border-0 w-screen h-10 md:w-40 md:h-32 md:rounded-xl md:m-2 md:p-4"
    :class="[active ? 'bg-red-300' : 'bg-gray-300']">{{ TrackRepository.getTrack(props.trackId).name }}</button></template>
