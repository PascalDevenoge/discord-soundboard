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
    <div v-if="searchable" class="flex flex-row justify-center">
      <input type="text" v-model="searchTerm" placeholder="Search for clip name..." class=" w-80 h-10 text-lg mb-6 py-2 px-4 border border-gray-300 rounded-xl">
      <button @click="searchTerm = ''" class="h-10 bg-blue-600 hover:bg-blue-500 rounded-xl text-white font-bold ml-2 px-5">Clear</button>
    </div>
    <p v-if="selectedTracks.length === 0" class="text-center text-lg m-4 text-gray-500">No tracks found...</p>
    <div class="flex flex-col md:flex-row justify-center flex-wrap">
      <SoundboardButton @rightClick="(id, x, y) => eventEmit('buttonRightClick', id, x, y)" v-for="id of selectedTracks" :key="id" :trackId="id"/>
    </div>
  </div>
</template>
