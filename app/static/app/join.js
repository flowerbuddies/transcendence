import { joinLobby } from '/static/app/game.js';
import { setBody } from '/static/app/index.js';

export function registerJoinForms() {
    document.querySelectorAll('.form-join').forEach((el) =>
        el.addEventListener('submit', async (ev) => {
            // prevent a page refresh
            ev.preventDefault();

            // register the join/create
            const formData = new FormData(ev.target);
            const joinRes = await fetch('/join', {
                method: 'POST',
                body: formData,
            });
            if (joinRes.status != 200) return alert(await joinRes.text());

            // switch to game view
            const lobbyName = formData.get('lobby-name');
            const playerName = formData.get('player-name');
            await setBody(`/game?lobby=${lobbyName}&player=${playerName}`);
            joinLobby(lobbyName, playerName);
        })
    );
}
