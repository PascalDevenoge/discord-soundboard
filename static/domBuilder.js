import {getVolume, setVolume} from "./storage.js";
import {playTrack} from "./api.js";

export function createButton(uuid, name) {
    const soundBite = document.createElement("div");
    const img = document.createElement("img");
    const slider = document.createElement("img");
    slider.setAttribute("data-uuid", uuid);
    slider.classList.add("soundSlider");

    soundBite.classList.add("soundBite");
    soundBite.appendChild(img);
    soundBite.appendChild(slider);
    soundBite.innerText = name;
    soundBite.setAttribute("data-uuid", uuid);

    slider.addEventListener("change", (e) => {
        setVolume(uuid, e.target.value)
    });

    soundBite.addEventListener("click", (e) => {
        playTrack(uuid, getVolume(uuid));
    }, false);

    return soundBite;
}