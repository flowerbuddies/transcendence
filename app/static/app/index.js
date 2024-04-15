import { registerJoinForms } from '/static/app/join.js';

history.replaceState('join', null);
registerJoinForms();

const closeWSConnsEvent = new Event('closeWSConns');

window.onpopstate = async (event) => {
    if (event.state === 'join') {
        await setBody('/join');
        registerJoinForms();
        document.dispatchEvent(closeWSConnsEvent);
    }
};

export async function setBody(url) {
    const res = await fetch(url);
    document.body.innerHTML = await res.text();
}
