let favoritesArr = JSON.parse(localStorage.getItem('favoritesArr')) ?? [];
let volumeConfig = JSON.parse(localStorage.getItem('volumeConfig')) ?? {};

export function getVolume(trackUUID) {
    return volumeConfig[trackUUID] ?? "1";
}

export function setVolume(trackUUID, volume) {
    volumeConfig[trackUUID] = volume;
    localStorage.setItem('volumeConfig', JSON.stringify(volumeConfig));
}

export function getFavorites() {
    return favoritesArr;
}

export function setFavorites(favOrder) {
    localStorage.setItem('favoritesArr', JSON.stringify(favOrder));
}