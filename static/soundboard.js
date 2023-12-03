let soundContainer = document.getElementById("soundBites");


let button = document.createElement("button", {id: `_button`})
let button2 = document.createElement("button", {id: `_button`})
let button3 = document.createElement("button", {id: `_button`})
button.innerText = "asdf"
button2.innerText = "asdf"
button3.innerText = "asdf"

button.classList.add("list-group-item,list-group-item-action");
button2.classList.add("list-group-item,list-group-item-action");
button3.classList.add("list-group-item,list-group-item-action");

soundContainer.appendChild(button);
soundContainer.appendChild(button2);
soundContainer.appendChild(button3)


tracks = fetch('tracks')
  .then(response => {
    if (!response.ok) {
      throw new Error("Failed to load available tracks")
    }
    return response.json()
  })
  .then(tracks => {
    for (let id in tracks) {
      let track_name = tracks[id];
      let button = document.createElement("button", {id: `${track_name}_button`})
      button.innerText = track_name
      button.classList.add("list-group-item,list-group-item-action");

      soundContainer.appendChild(button);
      button.addEventListener("click", () => {
        fetch(`play/${id}`)
      }, false)
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
