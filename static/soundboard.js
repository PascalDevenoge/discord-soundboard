let submitUpload = document.getElementById('submitUpload');
let favorites = document.getElementById('favorites');
let remainder = document.getElementById('remainder');
let canSortButton = document.getElementById('isSortable');

let isLocked = true;
let favoritesArr = JSON.parse(localStorage.getItem('favoritesArr'));
let remainderArr = JSON.parse(localStorage.getItem('remainderArr'));

favoritesArr = favoritesArr == null ? [] : favoritesArr;
remainderArr = remainderArr == null ? [] : remainderArr;

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
    .then(tracks => {
        const tracksMap = new Map(Object.entries(tracks));

        for (let track of favoritesArr) {
            let button = createButton(tracksMap.find((key, value) => value === track), track);
            favorites.appendChild(button);
        }

        for (let track of remainderArr) {
            let button = createButton(tracksMap.find((key, value) => value === track), track);
            remainder.appendChild(button);
        }

        for (let id in tracks) {
            if (tracksMap.find((key, value) => value === id) || tracksMap.find((key, value) => value === id)) {
                continue;
            }
            let button = createButton(id, tracks[id]);
            remainder.appendChild(button);
        }

        let nuclear_button = document.getElementById('nuclear_option');
        nuclear_button.addEventListener("click", () => {
            fetch(`play/all`)
        }, false)

        let stop_button = document.getElementById('stop')
        stop_button.addEventListener("click", () => {
            fetch("stop")
        })
    })

function createButton(id, name) {
    let button = document.createElement("a", {id: `${name}_button`});
    button.innerText = name;
    button.classList.add("list-group-item", "list-group-item-action", "soundBite");

    button.addEventListener("click", () => {
        fetch(`play/${id}`)
    }, false);
    return button;
}

canSortButton.addEventListener("click", (e) => {
    e.preventDefault();
    if (isLocked) {
        canSortButton.textContent = "Lock Order";
        isLocked = false;

        favoritesSort.option('disabled', false);
        remainderSort.option('disabled', false);
    } else {
        canSortButton.textContent = "Unlock Order";
        isLocked = true;

        favoritesSort.option('disabled', true);
        remainderSort.option('disabled', true);

        console.log(favoritesSort.options);

        let favoritesArr = [...favorites.children].filter(child => child.tagName === 'A').map(child => child.text);
        let remainderArr = [...remainder.children].filter(child => child.tagName === 'A').map(child => child.text);

        localStorage.setItem('favoritesArr', JSON.stringify(favoritesArr));
        localStorage.setItem('remainderArr', JSON.stringify(remainderArr));
    }
});
