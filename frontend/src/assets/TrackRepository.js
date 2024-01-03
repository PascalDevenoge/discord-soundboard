import { reactive, watch } from 'vue'

const tracks = reactive(new Map())

function addTrack (id, track) {
  tracks.set(id, track)
}

function deleteTrack (id) {
  tracks.delete(id)
}

function hasTrack (id) {
  return tracks.has(id)
}

function getTrack (id) {
  const track = tracks.get(id)
  return track === undefined ? null : track
}

function getAllTrackIds () {
  return [...tracks.keys()]
}

export default {
  addTrack,
  deleteTrack,
  hasTrack,
  getTrack,
  getAllTrackIds
}

function loadFavorites () {
  const storedData = localStorage.getItem('favorites')
  if (storedData == null) {
    localStorage.setItem('favorites', '[]')
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
      addTrack(track.id, { name: track.name, length: track.length, active: false, timeout: null, favorite: false })
    }
  })
  .then(() => {
    loadFavorites()
  })
  .then(() => {
    watch(tracks, async () => {
      const favoriteIds = []
      for (const [id, track] of tracks.entries()) {
        if (track.favorite) {
          favoriteIds.push(id)
        }
      }
      localStorage.setItem('favorites', JSON.stringify(favoriteIds))
    })
  })
  .then(() => {
    const sseSource = new EventSource('/listen')

    sseSource.addEventListener('clip-uploaded', event => {
      const eventData = JSON.parse(event.data)
      addTrack(eventData.id, { name: eventData.name, length: eventData.length, active: false, timeout: null, favorite: false })
      console.log(`Clip ${eventData.id}: ${eventData.name} was uploaded`)
    })

    sseSource.addEventListener('clip-deleted', event => {
      const eventData = JSON.parse(event.data)
      deleteTrack(eventData.id)
      console.log(`Clip ${eventData.id} was deleted`)
    })

    sseSource.addEventListener('clip-played', event => {
      const eventData = JSON.parse(event.data)
      const track = getTrack(eventData.id)

      if (track != null) {
        clearTimeout(track.timeout)
        track.active = true
        track.timeout = setTimeout(() => {
          track.active = false
        }, track.length)
      }
    })

    sseSource.addEventListener('all-clips-stopped', _ => {
      for (const [, data] of tracks.entries()) {
        clearTimeout(data.timeout)
        data.active = false
      }
    })

    sseSource.addEventListener('all-clips-played', _ => {
      for (const [, data] of tracks.entries()) {
        clearTimeout(data.timeout)
        data.active = true
        data.timeout = setTimeout(() => {
          data.active = false
        }, data.length)
      }
    })

    sseSource.addEventListener('clip-renamed', event => {
      const eventData = JSON.parse(event.data)
      const track = getTrack(eventData.id)
      if (track != null) {
        track.name = eventData.new_name
      }
    })

    sseSource.addEventListener('clip-stopped', event => {
      const eventData = JSON.parse(event.data)
      const track = getTrack(eventData.id)
      if (track != null) {
        clearTimeout(track.timeout)
        track.active = false
      }
    })
  })
  .catch(error => { console.error(error) })
