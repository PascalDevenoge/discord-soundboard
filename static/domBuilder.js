import {getVolume, setVolume} from "./storage.js";
import {playTrack} from "./api.js";

export function createButton(uuid, name) {
    const soundBite = document.createElement("div");
    const img = document.createElement("img");
    const slider = document.createElement("input");
    const nameElement = document.createElement("p");

    slider.setAttribute("data-uuid", uuid);
    slider.setAttribute("type", "range");
    slider.setAttribute("min", "0");
    slider.setAttribute("max", "10");
    slider.setAttribute("hidden", "true");
    slider.setAttribute("value", getVolume(uuid));
    slider.classList.add("soundSlider");
    soundBite.classList.add("soundBite");
    nameElement.classList.add("soundName");
    nameElement.innerText = name;
    soundBite.appendChild(img);
    soundBite.appendChild(slider);
    soundBite.appendChild(nameElement);
    soundBite.setAttribute("data-uuid", uuid);

    slider.addEventListener("change", (e) => {
        setVolume(uuid, e.target.value)
    });

    soundBite.addEventListener("click", (e) => {
        if (e.target.tagName === "INPUT") {
            return;
        }
        playTrack(uuid, getVolume(uuid));
    }, false);

    return soundBite;
}