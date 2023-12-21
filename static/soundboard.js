import {getTracks, playAllTracks, stopTracks} from "./api.js";
import {createButton} from "./domBuilder.js";
import {getFavorites, setFavorites} from "./storage.js";

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
        let favoriteOrder = getFavorites();

        for (let favUUID of favoriteOrder) {
            const trackUUID = Object.keys(tracksResponse).find(uuid => tracksResponse[uuid] === tracksResponse[favUUID]);
            const button = createButton(trackUUID, tracksResponse[favUUID]);
            favorites.appendChild(button);
        }

        for (let uuid in tracksResponse) {
            if (!favoriteOrder.includes(uuid)) {
                const button = createButton(uuid, tracksResponse[uuid]);
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

window.addEventListener("contextmenu", function (e) {
    let target = e.target;
    while (target !== null) {
        if (target.classList && target.classList.contains('soundBite')) {
            e.preventDefault();
            let contextMenu = document.getElementById("contextMenu");
            contextMenu.style.top = `${e.pageY}px`;
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.removeAttribute("hidden");
            return;
        }
        target = target.parentNode;
    }
});

window.addEventListener("click", function (e) {
    document.getElementById("contextMenu").setAttribute("hidden", "true");
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