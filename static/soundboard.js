let favorites = document.getElementById('favorites');
let remainder = document.getElementById('remainder');
let canSortButton = document.getElementById('isSortable');
let nuclear_button = document.getElementById('nuclear_option');
let stop_button = document.getElementById('stop')

let favoritesArr = JSON.parse(localStorage.getItem('favoritesArr')) ?? [];
let tracksObject = null;

let favoritesSort = new Sortable(favorites, {
    group: 'shared',
    filter: '.title',
    animation: 150,
    disabled: true
});

let remainderSort = new Sortable(remainder, {
    group: 'shared',
    filter: '.title',
    animation: 150,
    disabled: true
});

tracks = fetch('tracks')
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to load available tracks")
        }
        return response.json()
    })
    .then(tracksResponse => {
        tracksObject = tracksResponse;

        for (let favUUID of favoritesArr) {
            const trackUUID = Object.keys(tracksResponse).find(uuid => tracksResponse[uuid] === tracksResponse[favUUID]);
            const button = createButton(trackUUID, tracksResponse[favUUID]);
            favorites.appendChild(button);
        }

        for (let id in tracksResponse) {
            if (!favoritesArr.includes(id)) {
                const button = createButton(id, tracksResponse[id]);
                remainder.appendChild(button);
            }
        }

        nuclear_button.addEventListener("click", () => {
            fetch(`play/all`)
        }, false)

        stop_button.addEventListener("click", () => {
            fetch("stop")
        })
    })

function createButton(id, name) {
    const button = document.createElement("a", {id: `${name}_button`});
    button.innerText = name;
    button.classList.add("list-group-item", "list-group-item-action", "soundBite");
    button.setAttribute("data-uuid", id);

    button.addEventListener("click", () => {
        fetch(`play/${id}/1.0`)
    }, false);
    return button;
}

canSortButton.addEventListener("click", (e) => {
    e.preventDefault();
    if (favoritesSort.options.disabled) {
        canSortButton.textContent = "Lock Order";
        favoritesSort.option('disabled', false);
        remainderSort.option('disabled', false);
    } else {
        canSortButton.textContent = "Unlock Order";
        favoritesSort.option('disabled', true);
        remainderSort.option('disabled', true);

        let favOrder = [...favorites.children].filter(child => child.tagName === 'A')
            .map(child => child.getAttribute('data-uuid'));
        localStorage.setItem('favoritesArr', JSON.stringify(favOrder));
    }
});