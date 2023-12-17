import { html } from './deps.js';
import Dashboard from "./pages/Dashboard.js";

const App = () => {
    return (
        html`
            <div>
                <${Dashboard}/>
            </div>
        `
    );
}

export default App;