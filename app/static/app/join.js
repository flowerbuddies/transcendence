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
            await setBody('/game');
            joinLobby(
                formData.get('lobby-name'),
                formData.get('player-1-name'),
                formData.get('player-2-name')
            );
        })
    );
}
