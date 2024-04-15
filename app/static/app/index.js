import { gameSocket } from '/static/app/game.js';
import { registerJoinForms } from '/static/app/join.js';

history.replaceState('join', null);
registerJoinForms();

window.onpopstate = async (event) => {
    if (event.state === 'join') {
        await setBody('/join');
        registerJoinForms();
        gameSocket.close();
    }
};

export async function setBody(url) {
    const res = await fetch(url);
    document.body.innerHTML = await res.text();
}
