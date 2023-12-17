export function getTracks() {
    return fetch("/tracks")
        .then(checkStatus)
        .then(response => response.json());
}

export function playTrack(uuid, volume) {
    fetch(`play/${uuid}/${volume}`)
        .then(checkStatus);
}

export function playAllTracks() {
    fetch("play/all")
        .then(checkStatus);
}

export function stopTracks() {
    fetch("stop")
        .then(checkStatus);
}

function checkStatus(response) {
    if (response.status >= 200 && response.status < 300) {
        return response;
    } else {
        const error = new Error(response.statusText);
        error.response = response;
        throw error;
    }
}