import {html, React} from '../deps.js';
import {getTracks} from "../api.js";

const Dashboard = () => {

    let [tracks, setTracks] = React.useState([]);

    React.useEffect(() => {
        getTracks().then((tracks) => {
            setTracks(tracks);
            console.log(tracks);
        });
    }, []);


    console.log(tracks);
    return (
        html`
            <h1>The ultimate Discord Soundboard</h1>

            <div id="headerControls">
                <button id="playAllButton" type="button" className="btn btn-primary stuff">The nuclear option</button>
                <button id="stopButton" type="button" className="btn btn-danger stuff">Stop the insanity</button>
                <button id="sortUnlockButton" type="button" className="btn btn-primary stuff">Unlock Order</button>
                <button type="button" className="btn btn-primary stuff" data-bs-toggle="modal"
                        data-bs-target="#uploadDialog">Upload
                </button>
                <button type="button" className="btn btn-primary stuff" data-bs-toggle="modal"
                        data-bs-target="#volumeDialog">Volume
                </button>
            </div>

            <div id="soundboard">
                <div className="soundContainer">
                    <h2>Favorites</h2>
                    <div id="favorites">
                    </div>
                </div>
                <div className="soundContainer">
                    <h2>Remainder</h2>
                    <div id="remainder">
                    </div>
                </div>
            </div>
        `
    );
}

export default Dashboard;