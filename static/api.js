export function getTracks() {
    return fetch("/tracks")
        .then(checkStatus)
        .then(response => response.json());
}

export function getSequences() {
    return fetch("/sequences")
        .then(checkStatus)
        .then(response => response.json());
}

export function createSequence(sequence) {
    return fetch("/sequences", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(sequence)
    })
        .then(checkStatus)
        .then(response => response.json());
}

export function playSequence(id) {
    fetch(`/sequences/play/${id}`)
        .then(checkStatus);
}

export function removeSequence(id) {
    fetch(`/sequences/delete/${id}`, {
        method: "POST"
    })
        .then(checkStatus);
}

export function playTrack(uuid, volume) {
    fetch(`/play/${uuid}/${volume}.0`)
        .then(checkStatus);
}

export function playAllTracks() {
    fetch("/play/all")
        .then(checkStatus);
}

export function stopTracks() {
    fetch("/stop")
        .then(checkStatus);
}

export function uploadTrack() {
    // todo
}

export function uploadImage() {
    // todo do we even have a route for this?
}

export function renameTrack(uuid, newName) {
    fetch(`/rename/${uuid}/${newName}`, {
        method: "POST"
    })
        .then(checkStatus);
}

export function deleteTrack(uuid) {
    fetch(`/delete/${uuid}`, {
        method: "POST"
    }).then(checkStatus);
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