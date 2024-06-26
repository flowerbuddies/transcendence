import { registerJoinForms } from "/static/app/join.js";
import { registerPlayerOptionsUpdate } from "/static/app/options.js";

registerJoinForms();
registerPlayerOptionsUpdate();

const closeWSConnsEvent = new Event("closeWSConns");

window.onpopstate = async (event) => {
    if (event.state === "join") {
        await setBody("/join");
        registerJoinForms();
        registerPlayerOptionsUpdate();
        document.dispatchEvent(closeWSConnsEvent);
    }
};

export async function setBody(url) {
    const res = await fetch(url);
    document.body.innerHTML = await res.text();
}
