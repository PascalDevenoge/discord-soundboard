<script setup>
import TrackRepository from '@/assets/TrackRepository'
import { computed } from 'vue'

const props = defineProps({
  trackId: String,
  xOffset: Number,
  yOffset: Number
})

const xOffsetVal = computed(() => props.xOffset + 'px')
const yOffsetVal = computed(() => props.yOffset + 'px')

const isFavorite = computed(() => TrackRepository.getTrack(props.trackId).favorite)
function favoritesHandler () {
  const track = TrackRepository.getTrack(props.trackId)
  track.favorite = !track.favorite
}

function deleteHandler () {
  fetch('/delete/' + props.trackId, { method: 'POST' })
}

function stopHandler () {
  fetch('/stop/' + props.trackId)
}

const eventEmit = defineEmits('openSettings')
</script>

<template>
  <div id="container" class="absolute m-0 rounded-xl border border-gray-400 bg-gray-200">
    <div @click="stopHandler" class="h-11 py-2 px-5 hover:bg-gray-300 rounded-t-xl hover:cursor-pointer">
      <p class="align-middle text-lg">Stop playback</p>
    </div>
    <hr class="h-px border-x border-gray-300"/>
    <div @click="favoritesHandler" class="h-11 py-2 px-5 hover:bg-gray-300 rounded-t-xl hover:cursor-pointer">
      <p class="align-middle text-lg">{{ isFavorite ? 'Remove from favorites' : 'Add to favorites' }}</p>
    </div>
    <hr class="h-px border-x border-gray-300"/>
    <div @click="deleteHandler" class="h-11 py-2 px-5 hover:bg-gray-300 hover:cursor-pointer">
      <p class="align-middle text-lg">Delete clip</p>
    </div>
    <hr class="h-px border-x border-gray-300"/>
    <div @click="eventEmit('openSettings', props.trackId)" class="h-11 py-2 px-5 hover:bg-gray-300 rounded-b-xl hover:cursor-pointer">
      <p class="align-middle text-lg">Settings</p>
    </div>
  </div>
</template>

<style scoped>
  #container {
    left: v-bind('xOffsetVal');
    top: v-bind('yOffsetVal')
  }
</style>
