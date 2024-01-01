<script setup>
import { computed, ref } from 'vue'
import TrackRepository from '../assets/TrackRepository'
import SoundboardButton from './SoundboardButton.vue'

const props = defineProps({
  name: String,
  selectionPredicate: Function,
  searchable: {
    default: false,
    type: Boolean
  }
})

const eventEmit = defineEmits('buttonRightClick')

const searchTerm = ref('')

const selectedTracks = computed(() => {
  return TrackRepository.getAllTrackIds().filter(id => props.selectionPredicate(id)).filter(id => TrackRepository.getTrack(id).name.toLowerCase().includes(searchTerm.value.toLowerCase()))
})
</script>

<template>
  <div class="mb-5">
    <p class="text-3xl text-center mb-8">{{ props.name }}</p>
    <div class="flex justify-center">
      <input v-if="searchable" v-model="searchTerm" placeholder="Search for clip name..." class="align-middle w-80 h-10 text-lg mb-6 py-2 px-4 border border-gray-300 rounded-xl">
    </div>
    <p v-if="selectedTracks.length === 0" class="text-center text-lg m-4 text-gray-500">No tracks found...</p>
    <div class="flex flex-col md:flex-row justify-center flex-wrap">
      <SoundboardButton @rightClick="(id, x, y) => eventEmit('buttonRightClick', id, x, y)" v-for="id of selectedTracks" :key="id" :trackId="id"/>
    </div>
  </div>
</template>
