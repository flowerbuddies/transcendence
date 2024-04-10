export let gameSocket;

function initConn(lobbyName, playerName) {
    // TODO: add support for 2 players on the same window
    const key1 = 'q';
    const key2 = 'a';

    gameSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/lobby/' + lobbyName + '/'
    );

    gameSocket.onopen = () => {
        gameSocket.send(JSON.stringify({ type: 'init', player: playerName }));
    };

    gameSocket.onmessage = (e) => {
        const data = JSON.parse(e.data);

        if (data.type == 'players') {
            // players connected
            document.getElementById(
                'players-connected'
            ).textContent = `${data.players.length} / ${data.max}`;

            // players list
            const list = document.getElementById('players-list');
            let content = '';
            for (const player of data.players)
                content += `<li class="list-group-item list-group-item-${
                    player.is_eliminated ? 'danger' : 'success'
                }">${player.name} ${player.is_ai ? '🤖' : ''}</li>`;
            list.innerHTML = content;
        }
    };

    let isKey1Pressed = false;
    let isKey2Pressed = false;

    function keyPressed(ev) {
        if (ev.key === key1) {
            // send only one key event on `keydown`
            if (!isKey1Pressed)
                gameSocket.send(
                    JSON.stringify({
                        type: 'key',
                        key: 1,
                        player: playerName,
                    })
                );
            isKey1Pressed = true;
        } else if (ev.key === key2) {
            // send only one key event on `keydown`
            if (!isKey2Pressed)
                gameSocket.send(
                    JSON.stringify({
                        type: 'key',
                        key: 2,
                        player: playerName,
                    })
                );
            isKey2Pressed = true;
        }
    }

    function keyReleased(ev) {
        if (ev.key === key1) {
            gameSocket.send(
                JSON.stringify({
                    type: 'key',
                    key: 1,
                    player: playerName,
                })
            );
            isKey1Pressed = false;
        } else if (ev.key === key2) {
            gameSocket.send(
                JSON.stringify({
                    type: 'key',
                    key: 2,
                    player: playerName,
                })
            );
            isKey2Pressed = false;
        }
    }

    // we send the same event for both `keydown` and `keyup`
    // depending on the previous state, the server will be able to understand what's happening
    document.addEventListener('keydown', keyPressed);
    document.addEventListener('keyup', keyReleased);
}

function initScene() {
    // TODO: for now just print a black square
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
}

export function joinLobby(lobbyName, playerName) {
    initConn(lobbyName, playerName);
    initScene();
}
