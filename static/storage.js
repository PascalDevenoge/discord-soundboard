let favoritesArr = JSON.parse(localStorage.getItem('favoritesArr')) ?? [];
let volumeConfig = JSON.parse(localStorage.getItem('volumeConfig')) ?? {};
let tracks = [];

export function getVolume(trackUUID) {
    return volumeConfig[trackUUID] ?? "1";
}

export function setVolume(trackUUID, volume) {
    volumeConfig[trackUUID] = volume;
    localStorage.setItem('volumeConfig', JSON.stringify(volumeConfig));
}

export function removeVolume(trackUUID) {
    delete volumeConfig[trackUUID];
    localStorage.setItem('volumeConfig', JSON.stringify(volumeConfig));
}

export function getFavorites() {
    return favoritesArr;
}

export function setFavorites(favOrder) {
    localStorage.setItem('favoritesArr', JSON.stringify(favOrder));
}

export function removeFavorite(uuid) {
    favoritesArr = favoritesArr.filter(favUUID => favUUID !== uuid);
    localStorage.setItem('favoritesArr', JSON.stringify(favoritesArr));
}

export function setTracks(tracksResponse) {
    tracks = tracksResponse;
}

export function getAllTracks() {
    return tracks;
}

export function getTrackNames() {
    return tracks.map(track => track.name);
}

export function getTrackById(uuid) {
    return tracks.find(track => track.id === uuid) ?? {name: "Unknown Track"};
}