import {getAllSequences} from "../storage.js";

let sequenceList = document.getElementById('sequenceList');
let mainSequencer = document.getElementById('mainSequencer');
let sequenceCreator = document.getElementById('sequenceCreator');
let createSequenceButton = document.getElementById('createSequence');
let sequenceBackButton = document.getElementById('sequenceBack');
let allSequences = getAllSequences();

let exampleSequence = {
    name: "i will send you to jesus x4",
    tracks: [
        {
            uuid: "1234",
            volume: 1,
            delay: 0,
        },
        {
            uuid: "1234",
            volume: 1,
            delay: 100,
        },
        {
            uuid: "1234",
            volume: 1,
            delay: 50,
        },
        {
            uuid: "1234",
            volume: 1,
            delay: 0,
        },
    ]
}

export function initSequencer() {
    for (const sequence in allSequences) {
        sequenceList.appendChild(createSequence(sequence));
    }

    createSequenceButton.addEventListener("click", () => {
        mainSequencer.style.display = "none";
        sequenceCreator.style.display = "block";
    });

    sequenceBackButton.addEventListener("click", () => {
        mainSequencer.style.display = "block";
        sequenceCreator.style.display = "none";
    });
}

function createSequence(sequence) {
    const accordion = document.createElement('div');
    accordion.classList.add('accordion-item');
    accordion.innerHTML = `
        <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                    data-bs-target="#flush-collapseOne" aria-expanded="false"
                    aria-controls="flush-collapseOne">
                ${sequence.name}
            </button>
            <i class="fa-solid fa-play"></i>
            <i class="fa-solid fa-trash"></i>
        </h2>
        <div class="accordion-collapse collapse" aria-labelledby="flush-headingOne" data-bs-parent="#accordionFlushExample">
            <div class="accordion-body">
                ${createTrackList(sequence)}
            </div>
        </div>
    `;
    return accordion;
}

function createTrackList(sequence) {
    const trackList = document.createElement('div');
    trackList.classList.add('list-group');

    for (const track in sequence.tracks) {
        const entry = document.createElement('a');
        entry.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-start");
        entry.innerHTML = `
            <div class="ms-2 me-auto">
                <div class="fw-bold">${sequence.name}</div>
                Volume: ${track.volume}, Delay: ${track.delay}ms
            </div>
            <span class="badge bg-primary rounded-pill">14</span>
        `;
        trackList.appendChild(entry);
    }

    return trackList.outerHTML;
}