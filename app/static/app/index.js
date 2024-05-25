import { registerJoinForms } from "/static/app/join.js";
import { registerPlayerOptionsUpdate } from "/static/app/options.js";

registerJoinForms();
registerPlayerOptionsUpdate();

const closeWSConnsEvent = new Event("closeWSConns");

window.onpopstate = async (event) => {
    console.log(event.state);
    if (event.state === "join") {
        await setBody("/join");
        registerJoinForms();
        registerPlayerOptionsUpdate();
        document.dispatchEvent(closeWSConnsEvent);
    }
    if (event.state === "game") {
        //
    }
};

export async function setBody(url) {
    const res = await fetch(url);
    document.body.innerHTML = await res.text();
}
