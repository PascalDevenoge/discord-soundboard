let soundContainer = document.getElementById("soundBites");

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
