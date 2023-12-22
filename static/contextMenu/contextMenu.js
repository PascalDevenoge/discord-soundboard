import {deleteTrack, renameTrack} from "../api.js";
import {removeFavorite, removeVolume} from "../storage.js";

let uploadImageButton = document.getElementById('submitImageUpload')
let renameTrackButton = document.getElementById('submitTrackName')
let deleteTrackButton = document.getElementById('deleteTrack')
let trackImage = document.getElementById('trackImage')

let selectedTrackUUID = "";
let selectedTrack;

export function initContextMenu() {
    window.addEventListener("contextmenu", function (e) {
        let target = e.target;
        while (target !== null) {
            if (target.classList && target.classList.contains('soundBite')) {
                e.preventDefault();
                let contextMenu = document.getElementById("contextMenu");
                contextMenu.style.top = `${e.pageY}px`;
                contextMenu.style.left = `${e.pageX}px`;
                contextMenu.removeAttribute("hidden");
                selectedTrackUUID = target.getAttribute("data-uuid");
                selectedTrack = target;
                return;
            }
            target = target.parentNode;
        }
    });

    window.addEventListener("click", function (e) {
        document.getElementById("contextMenu").setAttribute("hidden", "true");
    });

    uploadImageButton.addEventListener("click", (e) => {
        let image = trackImage.files[0];
        // todo: upload image
    });

    renameTrackButton.addEventListener("click", (e) => {
        e.preventDefault();
        if (selectedTrackUUID === "") {
            return;
        }
        let newName = document.getElementById("trackName").value;
        renameTrack(selectedTrackUUID, newName);
        selectedTrack.getElementsByTagName("p")[0].textContent = newName;
        bootstrap.Modal.getInstance(document.getElementById('renameTrackDialog')).hide();
    });

    deleteTrackButton.addEventListener("click", (e) => {
        if (selectedTrackUUID === "") {
            return;
        }
        selectedTrack.remove();
        console.log(selectedTrack);
        deleteTrack(selectedTrackUUID);
        removeFavorite(selectedTrackUUID);
        removeVolume(selectedTrackUUID);
    });
}
