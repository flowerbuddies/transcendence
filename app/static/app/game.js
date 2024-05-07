import { setBody } from "/static/app/index.js";
let data = {};

function initConn(lobbyName, playerName, key1, key2) {
    const gameSocket = new WebSocket(
        "ws://" + window.location.host + "/ws/lobby/" + lobbyName + "/"
    );

    gameSocket.onopen = () => {
        gameSocket.send(JSON.stringify({ type: "init", player: playerName }));
    };

    gameSocket.onmessage = (e) => {
        data = JSON.parse(e.data);

        if (data.type == "players") {
            // players connected
            document.getElementById(
                "players-connected"
            ).textContent = `${data.players.length} / ${data.max}`;

            // players list
            const list = document.getElementById("players-list");
            let content = "";
            for (const player of data.players)
                content += `<li class="list-group-item list-group-item-${
                    player.is_eliminated ? "danger" : "success"
                }">${player.name} ${player.is_ai ? "🤖" : ""}</li>`;
            list.innerHTML = content;
        }
        //TODO translate
        if (data.type == "time") {
            let content = "";
            if (data.seconds != 0) content = `match in ${data.seconds}..`;
            document.getElementById("info").textContent = content;
        }
        //TODO translate 'balls missed' or remove
        //TODO make it be balls missed x/1 instead of x/3 for the tournament
        if (data.type == "scene") {
            data.scene.forEach((element) => {
                let score = "eliminated";
                if (element.type == "score" && element.score < 3)
                    score = ` balls missed ${element.score}/3`;
                if (
                    element.type == "score" &&
                    (element.side == "right" || element.side == "wall_right")
                )
                    if (!element.name) {
                        document.getElementById("score-right").textContent = "";
                    } else {
                        document.getElementById(
                            "score-right"
                        ).textContent = `(right) ${element.name}: ${score}`;
                    }
                if (
                    element.type == "score" &&
                    (element.side == "left" || element.side == "wall_left")
                )
                    if (!element.name) {
                        document.getElementById("score-left").textContent = "";
                    } else {
                        document.getElementById(
                            "score-left"
                        ).textContent = `(left) ${element.name}: ${score}`;
                    }
                if (
                    element.type == "score" &&
                    (element.side == "top" || element.side == "wall_top")
                )
                    if (!element.name) {
                        document.getElementById("score-top").textContent = "";
                    } else {
                        document.getElementById(
                            "score-top"
                        ).textContent = `(top) ${element.name}: ${score}`;
                    }
                if (
                    element.type == "score" &&
                    (element.side == "bottom" || element.side == "wall_bottom")
                )
                    if (!element.name) {
                        document.getElementById("score-bottom").textContent =
                            "";
                    } else {
                        document.getElementById(
                            "score-bottom"
                        ).textContent = `(bottom) ${element.name}: ${score}`;
                    }
            });
        }
        if (data.type == "next_match") {
            let content = "";
            if (data.players.length > 0) {
                content = "next match: ";
                for (let i = 0; i < data.amount; i++) {
                    if (data.players.length <= i) {
                        content += "???";
                    } else {
                        content += data.players[i];
                        data.players[i];
                    }
                    if (i + 1 != data.amount) {
                        content += " vs. ";
                    }
                }
            }
            document.getElementById("next-match").textContent = content;
        }
        //TODO translate
        if (data.type == "end") {
            document.getElementById("score-right").textContent = "";
            document.getElementById("score-left").textContent = "";
            document.getElementById("score-top").textContent = "";
            document.getElementById("score-bottom").textContent = "";
            document.getElementById(
                "winner"
            ).textContent = `${data.winner} won the match woo!`;
            const ctx = document.getElementById("canvas").getContext("2d");
            clearCanvas(ctx);
        }
        if (data.type == "winner") {
            document.getElementById(
                "winner"
            ).textContent = `${data.winner} won the tournament wowieee!!`;
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
                        type: "key",
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
                        type: "key",
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
                    type: "key",
                    key: 1,
                    player: playerName,
                })
            );
            isKey1Pressed = false;
        } else if (ev.key === key2) {
            gameSocket.send(
                JSON.stringify({
                    type: "key",
                    key: 2,
                    player: playerName,
                })
            );
            isKey2Pressed = false;
        } else if (ev.key === "Escape") {
            closeGameConnection();
        }
    }

    async function closeGameConnection() {
        document.removeEventListener("keydown", keyPressed);
        document.removeEventListener("keyup", keyReleased);
        document.removeEventListener("closeWSConns", () => gameSocket.close());
        gameSocket.close();
        await setBody("/join");
    }

    // we send the same event for both `keydown` and `keyup`
    // depending on the previous state, the server will be able to understand what's happening
    document.addEventListener("keydown", keyPressed);
    document.addEventListener("keyup", keyReleased);
    document.addEventListener("closeWSConns", () => gameSocket.close());
}

function initScene() {
    const ctx = document.getElementById("canvas").getContext("2d");

    window.requestAnimationFrame(renderLoop);

    function renderLoop() {
        clearCanvas(ctx);
        drawScene(data.scene, ctx);
        window.requestAnimationFrame(renderLoop);
    }
}

export function joinLobby(lobbyName, player1Name, player2Name) {
    initConn(lobbyName, player1Name, "ArrowUp", "ArrowDown");
    if (player2Name) initConn(lobbyName, player2Name, "q", "a");
    initScene();
}

function clearCanvas(ctx) {
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
}

function drawScene(scene, ctx) {
    if (!scene) return;
    scene.forEach((element) => {
        if (element.color) {
            ctx.fillStyle = element.color;
        } else {
            ctx.fillStyle = "white";
        }
        ctx.fillRect(
            ctx.canvas.width * element.x,
            ctx.canvas.height * element.y,
            ctx.canvas.width * element.width,
            ctx.canvas.height * element.height
        );
    });
}

// check performance
let startTime = performance.now();
let frames = 0;

function updateFPS() {
    frames++;
    const currentTime = performance.now();
    const delta = currentTime - startTime;

    if (delta >= 1000) {
        console.log("FPS:", frames);
        frames = 0;
        startTime = currentTime;
    }
}
