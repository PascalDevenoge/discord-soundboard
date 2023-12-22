import {getTracks, playAllTracks, stopTracks} from "./api.js";
import {createButton} from "./soundBiteBuilder.js";
import {getAllTracks, getFavorites, getTrackById, setFavorites, setTracks} from "./storage.js";
import {initContextMenu} from "./contextMenu/contextMenu.js";

let favorites = document.getElementById('favorites');
let remainder = document.getElementById('remainder');
let canSortButton = document.getElementById('sortUnlockButton');
let nuclearButton = document.getElementById('playAllButton');
let stopButton = document.getElementById('stopButton')

let favoritesSort = new Sortable(favorites, {
    group: 'shared',
    filter: function (evt, target) {
        return (target.classList.contains('title') ||
            target.classList.contains('soundSlider'));
    },
    animation: 150,
    disabled: true
});

let remainderSort = new Sortable(remainder, {
    group: 'shared',
    filter: function (evt, target) {
        return (target.classList.contains('title') ||
            target.classList.contains('soundSlider'));
    },
    animation: 150,
    disabled: true
});

getTracks()
    .then(tracksResponse => {
        setTracks(tracksResponse);

        for (let trackUUID of getFavorites()) {
            const button = createButton(trackUUID, getTrackById(trackUUID).name, undefined);
            favorites.appendChild(button);
        }

        for (let track of getAllTracks()) {
            if (!getFavorites().includes(track.id)) {
                const button = createButton(track.id, track.name, undefined);
                remainder.appendChild(button);
            }
        }
    });

nuclearButton.addEventListener("click", () => {
    playAllTracks();
});

stopButton.addEventListener("click", () => {
    stopTracks();
});

canSortButton.addEventListener("click", (e) => {
    e.preventDefault();
    let allSliders = document.getElementsByClassName("soundSlider");
    if (favoritesSort.options.disabled) {
        canSortButton.textContent = "Lock Order";
        Array.from(allSliders).forEach(slider => slider.removeAttribute("hidden"));
        favoritesSort.option('disabled', false);
        remainderSort.option('disabled', false);
    } else {
        canSortButton.textContent = "Unlock Order";
        Array.from(allSliders).forEach(slider => slider.setAttribute("hidden", "true"));
        favoritesSort.option('disabled', true);
        remainderSort.option('disabled', true);

        let favOrder = [...favorites.children].filter(child => child.tagName === 'DIV').map(child => child.getAttribute('data-uuid'));
        setFavorites(favOrder);
    }
});

initContextMenu();