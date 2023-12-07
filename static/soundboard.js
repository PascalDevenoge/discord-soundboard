let favorites = document.getElementById('favorites');
let remainder = document.getElementById('remainder');
let canSortButton = document.getElementById('isSortable');
let nuclear_button = document.getElementById('nuclear_option');
let stop_button = document.getElementById('stop')
let volumeList = document.getElementById('volumeList')

let favoritesArr = JSON.parse(localStorage.getItem('favoritesArr')) ?? [];
let volumeConfig = JSON.parse(localStorage.getItem('volumeConfig')) ?? [];
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
    }).then(() => {
        for (let [uuid, name] of Object.entries(tracksObject)) {
            let listItem = document.createElement("li");
            listItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
            listItem.textContent = name;

            let slider = document.createElement("input");
            slider.type = "range";
            slider.classList.add("slider");
            slider.setAttribute("data-uuid", uuid);
            listItem.appendChild(slider);
            volumeConfig.appendChild(listItem);

            slider.addEventListener("change", (e) => {
                let trackUUID = e.target.getAttribute("data-uuid");
                let volume = e.target.value;
                volumeConfig[trackUUID] = volume;
                localStorage.setItem('volumeConfig', JSON.stringify(volumeConfig));
            });
        }
    });

function createButton(id, name) {
    const button = document.createElement("a", {id: `${name}_button`});
    button.innerText = name;
    button.classList.add("list-group-item", "list-group-item-action", "soundBite");
    button.setAttribute("data-uuid", id);

    button.addEventListener("click", (e) => {
        let trackUUID = e.target.getAttribute("data-uuid");
        let volume = volumeConfig[trackUUID] ?? 1.0;
        fetch(`play/${id}/${volume}`);
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