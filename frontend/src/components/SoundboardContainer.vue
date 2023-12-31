<script setup>
  import { computed } from 'vue';
import TrackRepository from '../assets/TrackRepository';
  import SoundboardButton from './SoundboardButton.vue'

  const props = defineProps({
    name
  })

  const nonFavorites = computed(() => {
    return TrackRepository.getAllTrackIds().filter(id => !TrackRepository.getTrack(id).favorite)
  })

  function buttonRightClickHandler(id) {
    TrackRepository.addFavorite(id)
  }
</script>

<template>
  <div>
    <p class="text-3xl text-center pb-8">{{ props.name }}</p>
    <div class="flex flex-col md:flex-row justify-center flex-wrap">
      <SoundboardButton v-for="id of nonFavorites" :trackId="id" :right-click-action="buttonRightClickHandler"/>
    </div>
  </div>
</template>
