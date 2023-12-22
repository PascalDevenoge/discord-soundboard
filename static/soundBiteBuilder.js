import {getVolume, setVolume} from "./storage.js";
import {playTrack} from "./api.js";

export function createButton(uuid, name, img) {
    const soundBite = document.createElement("div");
    soundBite.classList.add("soundBite");
    soundBite.appendChild(createImage(img));
    soundBite.appendChild(createSlider(uuid));
    soundBite.appendChild(createText(name));
    soundBite.setAttribute("data-uuid", uuid);

    soundBite.addEventListener("click", (e) => {
        if (e.target.tagName === "INPUT") {
            return;
        }
        playTrack(uuid, getVolume(uuid));
    }, false);

    return soundBite;
}

function createSlider(uuid) {
    const slider = document.createElement("input");
    slider.setAttribute("data-uuid", uuid);
    slider.setAttribute("type", "range");
    slider.setAttribute("min", "0");
    slider.setAttribute("max", "10");
    slider.setAttribute("hidden", "true");
    slider.setAttribute("value", getVolume(uuid));
    slider.classList.add("soundSlider");

    slider.addEventListener("change", (e) => {
        setVolume(uuid, e.target.value)
    });

    return slider;
}

function createText(trackName) {
    const name = document.createElement("p");
    name.classList.add("soundName");
    name.innerText = trackName;
    return name;
}

function createImage(trackImg) {
    const img = document.createElement("img");
    if (trackImg !== undefined) {
        // todo add img to button
    }
    return img;
}