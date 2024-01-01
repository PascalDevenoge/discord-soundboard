<script setup>
import { computed, ref } from 'vue'

import SoundboardContainer from './components/SoundboardContainer.vue'
import HeaderButton from './components/HeaderButton.vue'
import ModalDialog from './components/ModalDialog.vue'
import ButtonContextMenu from './components/ButtonContextMenu.vue'
import TrackRepository from './assets/TrackRepository'

function backendRequest (target) {
  fetch(target)
    .then(response => {
      if (!response.ok) {
        // eslint-disable-next-line no-undef
        console.error(`Request to ${props.target_route} failed. ${response.statusText}: ${response.body}`)
      }
    })
}

function uploadFile () {
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

function buttonRightClickHandler (trackId, xOffset, yOffset) {
  contextMenuOpen.value = true
  contextMenuOffsetX.value = xOffset
  contextMenuOffsetY.value = yOffset
  contextMenuTrackId.value = trackId
}

function openSettingsHandler (trackId) {
  contextMenuOpen.value = false
  settingsDialogTrackId.value = trackId
  settingsDialogOpen.value = true
}

window.addEventListener('click', () => {
  contextMenuOpen.value = false
})

window.addEventListener('contextmenu', e => { e.preventDefault() })

const contextMenuOpen = ref(false)
const contextMenuTrackId = ref()
const contextMenuOffsetX = ref(0)
const contextMenuOffsetY = ref(0)

const uploadDialogOpen = ref(false)

const settingsDialogOpen = ref(false)
const settingsDialogTrackId = ref()
const settingsDialogTrackTitle = computed(() => 'Settings for ' + TrackRepository.getTrack(settingsDialogTrackId.value).name)
</script>

<template>
  <div>
    <p class="text-4xl md:text-6xl italic text-center py-6 md:py-12">The ultimate Discord Soundboard</p>
    <div class="flex md:flex-row flex-col justify-center">
      <HeaderButton @click="backendRequest('/play/all')">The nuclear option</HeaderButton>
      <HeaderButton @click="backendRequest('/stop/all')" :highlighted="true">Stop all</HeaderButton>
      <HeaderButton @click="uploadDialogOpen = true">Upload</HeaderButton>
    </div>
    <div class="pt-16 grid justify-center grid-cols-1 md:grid-cols-1 gap-10">
      <hr class="h-px border-x border-gray-300"/>
      <SoundboardContainer @buttonRightClick="buttonRightClickHandler" :name="'Favorites'" :selection-predicate="(id) => TrackRepository.getTrack(id).favorite"/>
      <hr class="h-px border-x border-gray-300"/>
      <SoundboardContainer @buttonRightClick="buttonRightClickHandler" :name="'Uncategorized'" :selection-predicate="(id) => !TrackRepository.getTrack(id).favorite" :searchable="true"/>
    </div>
    <ModalDialog v-if="uploadDialogOpen" @close="uploadDialogOpen = false" :title="'Upload clip'" :ok-action="uploadFile">
      <input id="uploadClipFile" class="block w-full h-10 border border-gray-300 rounded-lg file:rounded-l-lg file:border-none file:text-white file:font-semibold file:bg-blue-600 file:hover:bg-blue-500 file:h-10 file:w-24 file:mr-3" type="file"/>
    </ModalDialog>
    <ButtonContextMenu @openSettings="openSettingsHandler" v-if="contextMenuOpen" :trackId="contextMenuTrackId" :x-offset="contextMenuOffsetX" :y-offset="contextMenuOffsetY"/>
    <ModalDialog v-if="settingsDialogOpen" @close="settingsDialogOpen = false" :title="settingsDialogTrackTitle" :ok-action="() => {}">
      <label for="default-range" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Volume</label>
      <input id="default-range" type="range" min="-30" max="30" value="0" step="0.1" class="">
    </ModalDialog>

    <div>
      <p class="float-right m-4 text-gray-500">© {{ new Date().getFullYear() }} Pascal Devenoge, Felix Tran</p>
    </div>
  </div>
</template>
