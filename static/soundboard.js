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
      document.body.appendChild(button)
      document.body.appendChild(document.createElement("br"))
      button.addEventListener("click", () => {
        fetch(`play/${id}`)
      }, false)
    }
  })