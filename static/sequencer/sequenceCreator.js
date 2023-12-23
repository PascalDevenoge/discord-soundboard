import {getTrackNames} from "../storage.js";
import {createSequence} from "../api.js";

let sequenceCreator = document.getElementById('sequenceCreator');
let sequenceFinishButton = document.getElementById('sequenceFinish');
let trackNames = getTrackNames();

export function createSequenceBuilder() {
    const sequence = document.createElement('div');
    sequence.appendChild(createSequenceHeader());

    sequenceFinishButton.addEventListener("click", () => {
        let sequence = {
            name: document.getElementById('sequenceName').value,
            tracks: [],
        }
        for (let entry of document.getElementsByClassName('sequenceEntry')) {
            let track = {
                uuid: entry.getElementsByClassName('sequenceVolumeDropdown')[0].value,
                volume: entry.getElementsByClassName('sequenceEntryVolume')[0].value,
                delay: entry.getElementsByClassName('sequenceEntryDelay')[0].value,
            };
            sequence.tracks.push(track);
        }

        console.log(sequence)
        createSequence(sequence).then(id => {
            // todo do something with return value
        });
    });

    return sequence;
}

export function createSequenceEntry() {
    const entry = document.createElement('div');
    entry.classList.add('sequenceEntry');
    entry.innerHTML = `
        ${createSequenceDropdown()}
        <p class="trackLength"></p>
        <input class="sequenceEntryVolume form-control" type="text" placeholder="Volume">
        <input class="sequenceEntryDelay form-control" type="text" placeholder="Delay">
    `;
    entry.appendChild(createDeleteButton());

    return entry;
}

function createSequenceHeader() {
    const sequenceHeader = document.createElement('div');
    const sequenceName = document.createElement('input');
    const addEntry = document.createElement('button');
    sequenceHeader.classList.add('sequenceHeader');
    sequenceName.classList.add('form-control');
    sequenceName.id = 'sequenceName';
    sequenceName.setAttribute('type', 'text');
    sequenceName.setAttribute('placeholder', 'Sequence name');
    sequenceHeader.appendChild(sequenceName);
    sequenceHeader.appendChild(addEntry);
    addEntry.classList.add('btn', 'btn-primary');
    addEntry.innerText = '+';

    addEntry.addEventListener('click', () => {
        sequenceCreator.appendChild(createSequenceEntry());
        $('.sequenceVolumeDropdown').select2({
            placeholder: $(this).data('placeholder'),
            dropdownParent: $('#sequenceDialog'),
        });
    });
    return sequenceHeader;
}

function createSequenceDropdown() {
    const dropdown = document.createElement('select');
    dropdown.classList.add('sequenceVolumeDropdown');
    dropdown.setAttribute('data-placeholder', 'Choose track');

    const option = document.createElement('option');
    option.innerText = "asfdasd";
    dropdown.appendChild(option);

    const option2 = document.createElement('option');
    option2.innerText = "asfdasdasdfasfadsfdasfafdsfasdfasdfddf";
    dropdown.appendChild(option2);

    for (const track of trackNames) {
        const option = document.createElement('option');
        option.innerText = track;
        dropdown.appendChild(option);
    }
    return dropdown.outerHTML;
}

function createDeleteButton() {
    const deleteButton = document.createElement('button');
    deleteButton.classList.add('fa-solid', 'fa-trash');

    deleteButton.addEventListener('click', () => {
        deleteButton.parentElement.remove();
    });

    return deleteButton;
}