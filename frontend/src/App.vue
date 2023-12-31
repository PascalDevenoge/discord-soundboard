<script setup>
import { ref } from 'vue'

import FavoritesContainer from './components/FavoritesContainer.vue';
import SoundboardContainer from './components/SoundboardContainer.vue';
import HeaderButton from './components/HeaderButton.vue';
import Modal from './components/Modal.vue';

function backendRequest(target) {
  fetch(target)
    .then(response => {
      if (!response.ok) {
        console.error(`Request to ${props.target_route} failed. ${response.statusText}: ${response.body}`)
      }
    })
}

function uploadFile() {
  const formData = new FormData()
  formData.append('file', document.getElementById('uploadClipFile').files[0])
  fetch('/upload', {
    method: 'post',
    body: formData
  })
    .then(response => {
      if (!response.ok) {
        console.error(`Failed to upload file. ${response.statusText}: ${response.body}`)
      }
    })
}

const uploadDialogOpen = ref(false)
</script>

<template>
  <div>
    <p class="text-4xl md:text-6xl italic text-center py-6 md:py-12">The ultimate Discord Soundboard</p>
    <div class="flex md:flex-row flex-col justify-center">
      <HeaderButton @click="backendRequest('/play/all')">The nuclear option</HeaderButton>
      <HeaderButton @click="backendRequest('/stop')" :highlighted="true">Stop all</HeaderButton>
      <HeaderButton @click="uploadDialogOpen = true">Upload</HeaderButton>
    </div>
    <div class="pt-5 grid justify-center grid-cols-1 md:grid-cols-2 gap-10">
      <FavoritesContainer :name="'Favorites'" />
      <SoundboardContainer :name="'Uncategorized'" />
    </div>
    <Modal v-if="uploadDialogOpen" @close="uploadDialogOpen = false" :title="'Upload clip'" :ok-action="uploadFile">
      <input id="uploadClipFile" class="my-3 block w-full h-10 border border-gray-300 rounded-lg file:rounded-l-lg file:border-none file:text-white file:font-semibold file:bg-blue-600 file:hover:bg-blue-500 file:h-10 file:w-24 file:mr-3" type="file"/>
    </Modal>
  </div>
</template>
