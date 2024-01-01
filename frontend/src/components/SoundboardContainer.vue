<script setup>
import { computed } from 'vue'
import TrackRepository from '../assets/TrackRepository'
import SoundboardButton from './SoundboardButton.vue'

const props = defineProps({
  name: String,
  selectionPredicate: Function
})

const eventEmit = defineEmits('buttonRightClick')

const selectedTracks = computed(() => {
  return TrackRepository.getAllTrackIds().filter(id => props.selectionPredicate(id))
})
</script>

<template>
  <div>
    <p class="text-3xl text-center pb-8">{{ props.name }}</p>
    <div class="flex flex-col md:flex-row justify-center flex-wrap">
      <SoundboardButton @rightClick="(id, x, y) => eventEmit('buttonRightClick', id, x, y)" v-for="id of selectedTracks" :key="id" :trackId="id"/>
    </div>
  </div>
</template>
