import {createSequenceBuilder} from "./sequenceCreator.js";
import {deleteSequence, getSequences, playSequence} from "../api.js";
import {getTrackById} from "../storage.js";

let sequenceList = document.getElementById('sequenceList');
let mainSequencer = document.getElementById('mainSequencer');
let sequenceCreator = document.getElementById('sequenceCreator');
let createSequenceButton = document.getElementById('createSequence');
let sequenceBackButton = document.getElementById('sequenceBack');

export function initSequencer() {
    getSequences()
        .then(allSequences => {
            for (const sequence of allSequences) {
                let node = createSequenceDialog(sequence);
                sequenceList.appendChild(node);

                node.getElementsByClassName('playSequence')[0].addEventListener('click', () => {
                    playSequence(sequence.id);
                });
                node.getElementsByClassName('deleteSequence')[0].addEventListener('click', () => {
                    deleteSequence(sequence.id);
                });
            }
        });

    sequenceCreator.appendChild(createSequenceBuilder());

    createSequenceButton.addEventListener("click", () => {
        mainSequencer.style.display = "none";
        sequenceCreator.style.display = "block";
    });

    sequenceBackButton.addEventListener("click", () => {
        mainSequencer.style.display = "block";
        sequenceCreator.style.display = "none";
    });
}

function createSequenceDialog(sequence) {
    const accordion = document.createElement('div');
    accordion.classList.add('accordion-item');
    accordion.setAttribute("sequenceId", sequence.id);
    accordion.innerHTML = `
        <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                    data-bs-target="#${sequence.name.replace(" ", "")}" aria-expanded="false"
                    aria-controls="${sequence.name}.replace(" ", "")">
                ${sequence.name}
            </button>
            <button class="fa-solid fa-play playSequence"></button>
            <button class="fa-solid fa-trash deleteSequence"></button>
        </h2>
        <div id="${sequence.name.replace(" ", "")}" class="accordion-collapse collapse" aria-labelledby="flush-headingOne" data-bs-parent="#accordionFlushExample">
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

    for (const track of sequence.tracks) {
        const entry = document.createElement('a');
        entry.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-start");
        entry.innerHTML = `
            <div class="ms-2 me-auto">
                <div class="fw-bold">${getTrackById(track.uuid).name}</div>
                Volume: ${track.volume}, Delay: ${track.delay}ms
            </div>
        `;
        trackList.appendChild(entry);
    }

    return trackList.outerHTML;
}