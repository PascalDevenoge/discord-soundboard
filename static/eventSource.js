const eventSource = new EventSource("listen");

eventSource.addEventListener("play-clip", (event) => {
    const id = JSON.parse(event.data).id;
    console.log(`Played clip ${id}`)
})

eventSource.addEventListener("play-all", (event) => {
    console.log("Played all clips")
})

eventSource.addEventListener("stop-all", (event) => {
    console.log("Stopped playback")
})

eventSource.onerror = (err) => {
    console.error("EventSource error:", err)
}