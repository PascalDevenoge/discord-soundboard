import { reactive } from 'vue'

let tracks = reactive(new Map())

function addTrack(id, track) {
  tracks.set(id, track)
}

function deleteTrack(id) {
  deleteFavorite(id)
  tracks.delete(id)
}

function hasTrack(id) {
  return tracks.has(id)
}

function getTrack(id) {
  const track = tracks.get(id)
  return track == undefined ? null : track
}

function getAllTrackIds() {
  return [...tracks.keys()]
}

function addFavorite(id) {
  const track = getTrack(id)
  if (track == null) return

  track.favorite = true
  updateFavoritesStorage()
}

function deleteFavorite(id) {
  const track = getTrack(id)
  if (track == null) return

  track.favorite = false
  updateFavoritesStorage()
}

export default {
  addTrack,
  deleteTrack,
  hasTrack,
  getTrack,
  getAllTrackIds,
  addFavorite,
  deleteFavorite,
}

function updateFavoritesStorage() {
  let favoriteIds = []
  for (const [id, track] of tracks.entries()) {
    if (track.favorite) {
      favoriteIds.push(id)
    }
  }
  localStorage.setItem('favorites', JSON.stringify(favoriteIds))
}

function loadFavorites() {
  const storedData = localStorage.getItem('favorites')
  if (storedData == null) {
    localStorage.setItem('favorites', [])
    return
  }
  const favoriteIds = JSON.parse(storedData)
  const purgedIds = favoriteIds.filter(id => hasTrack(id))
  localStorage.setItem('favorites', JSON.stringify(purgedIds))

  for (const id of purgedIds) {
    getTrack(id).favorite = true
  }
}

fetch('/tracks')
  .then(response => {
    if (!response.ok) {
      throw new Error(`Could not load tracks. ${response.statusText}: ${response.body}`)
    }
    return response.json()
  })
  .then(tracks => {
    for (const track of tracks) {
      addTrack(track.id, { name: track.name, length: track.length, active: false, favorite: false })
    }
  })
  .then(() => {
    loadFavorites()
  })
  .then(() => {
    const sseSource = new EventSource('/listen')

    sseSource.addEventListener('clip-uploaded', event => {
      const eventData = JSON.parse(event.data)
      addTrack(eventData.id, { name: eventData.name, length: eventData.length, active: false, favorite: false})
      console.log(`Clip ${eventData.id}: ${eventData.name} was uploaded`)
    })

    sseSource.addEventListener('clip-deleted', event => {
      const eventData = JSON.parse(event.data)
      deleteTrack(eventData.id)
      console.log(`Clip ${eventData.id} was deleted`)
    })
  })
  .catch(error => { console.error(error) })
