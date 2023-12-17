import {html, React, ReactDOM} from "./deps.js";
import App from "./App.js";

ReactDOM.render(
    html`
        <${App}/>
    `,
    document.getElementById('root'),
)