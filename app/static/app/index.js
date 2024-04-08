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

        // get the game view
        const gameRes = await fetch(
            `/game?lobby=${formData.get('lobby-name')}&player=${formData.get(
                'player-name'
            )}`
        );

        // get the lobby and player values
        const queryString = new URL(gameRes.url).search;
        const urlParams = new URLSearchParams(queryString);

        window.lobbyName = urlParams.get('lobby');
        window.playerName = urlParams.get('player');

        // set the game view
        document.body.innerHTML = await gameRes.text();

        // game script
        let scriptElement = document.createElement('script');
        scriptElement.src = '/static/app/game.js';
        document.body.appendChild(scriptElement);
    })
);
