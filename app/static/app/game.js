import { setBody } from "/static/app/index.js";
import { registerJoinForms } from "/static/app/join.js";
import { registerPlayerOptionsUpdate } from "/static/app/options.js";
let data = {};
let playerOneName;
let playerTwoName;

function initConn(lobbyName, playerName, key1, key2) {
    const gameSocketProtocol =
        window.location.protocol === "https:" ? "wss:" : "ws:";
    const gameSocket = new WebSocket(
        gameSocketProtocol +
            "//" +
            window.location.host +
            "/ws/lobby/" +
            lobbyName +
            "/"
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
        if (data.type == "time") {
            let content = "";
            if (data.seconds != 0) content = `${data.string}`;
            document.getElementById("info").textContent = content;
        }
        if (data.type == "scene") {
            data.scene.forEach((element) => {
                if (element.type != "score") return;
                let status = `: ${element.elimination_msg}`;
                if (data.is_tournament && element.score < 1) {
                    status = "";
                } else if (!data.is_tournament && element.score < 3)
                    status = `: ${element.ball_msg}`;
                if (element.side == "right" || element.side == "wall_right")
                    if (!element.name) {
                    } else {
                        document
                            .getElementById("right-icon")
                            .classList.remove("d-none");
                        document.getElementById(
                            "score-right"
                        ).textContent = `${element.name}${status}`;
                    }
                if (element.side == "left" || element.side == "wall_left")
                    if (!element.name) {
                    } else {
                        document
                            .getElementById("left-icon")
                            .classList.remove("d-none");
                        document.getElementById(
                            "score-left"
                        ).textContent = `${element.name}${status}`;
                    }
                if (element.side == "top" || element.side == "wall_top")
                    if (!element.name) {
                    } else {
                        document
                            .getElementById("top-icon")
                            .classList.remove("d-none");
                        document.getElementById(
                            "score-top"
                        ).textContent = `${element.name}${status}`;
                    }
                if (element.side == "bottom" || element.side == "wall_bottom")
                    if (!element.name) {
                    } else {
                        document
                            .getElementById("bottom-icon")
                            .classList.remove("d-none");
                        document.getElementById(
                            "score-bottom"
                        ).textContent = `${element.name}${status}`;
                    }
            });
        }
        if (data.type == "readiness") {
            let status = data.msg;
            if (!data.ready) {
                document.getElementById("info").textContent = data.info_msg;
                if (data.name == playerOneName)
                    status = `${data.press_msg} ↑ ${data.or_msg} ↓`;
                if (data.name == playerTwoName)
                    status = `${data.press_msg} Q ${data.or_msg} A`;
            }
            if (data.side == "right")
                document.getElementById(
                    "score-right"
                ).textContent = `${data.name}: ${status}`;
            if (data.side == "left")
                document.getElementById(
                    "score-left"
                ).textContent = `${data.name}: ${status}`;
            if (data.side == "top")
                document.getElementById(
                    "score-top"
                ).textContent = `${data.name}: ${status}`;
            if (data.side == "bottom")
                document.getElementById(
                    "score-bottom"
                ).textContent = `${data.name}: ${status}`;
        }
        if (data.type == "next_match") {
            let content = "";
            if (data.players.length > 0) {
                content = `${data.string}: `;
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
        if (data.type == "end") {
            document.getElementById("winner").textContent = `${data.winner}`;
            const ctx = document.getElementById("canvas").getContext("2d");
            clearCanvas(ctx);
        }
        if (data.type == "winner") {
            document.getElementById("winner").textContent = `${data.winner}`;
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
            data = {};
            closeGameConnection();
            goBackToJoin();
        }
    }

    function closeGameConnection() {
        document.removeEventListener("keydown", keyPressed);
        document.removeEventListener("keyup", keyReleased);
        document.removeEventListener("closeWSConns", () => gameSocket.close());
        gameSocket.close();
    }

    async function goBackToJoin() {
        await setBody("/join");
        registerJoinForms();
        registerPlayerOptionsUpdate();
    }

    // we send the same event for both `keydown` and `keyup`
    // depending on the previous state, the server will be able to understand what's happening
    document.addEventListener("keydown", keyPressed);
    document.addEventListener("keyup", keyReleased);
    document.addEventListener("closeWSConns", closeGameConnection);
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
    document.getElementById("score-right").textContent = "";
    document.getElementById("score-left").textContent = "";
    document.getElementById("score-top").textContent = "";
    document.getElementById("score-bottom").textContent = "";
    document.getElementById(
        "player-one-keys"
    ).textContent = `${player1Name}: ↑ ↓`;
    playerOneName = player1Name;
    initConn(lobbyName, player1Name, "ArrowUp", "ArrowDown");
    if (player2Name) {
        document.getElementById(
            "player-two-keys"
        ).textContent = `${player2Name}: Q A`;
        playerTwoName = player2Name;
        initConn(lobbyName, player2Name, "q", "a");
    }
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
