export function join(gameName, playerName) {
  document.getElementById("join-view").classList.add("d-none");
  document.getElementById("game-view").classList.remove("d-none");

  const keyMappings = {
    w: { key: 1, side: "left" },
    s: { key: 2, side: "left" },
    ArrowUp: { key: 3, side: "right" },
    ArrowDown: { key: 4, side: "right" },
    a: { key: 5, side: "top" },
    d: { key: 6, side: "top" },
    ArrowLeft: { key: 7, side: "bottom" },
    ArrowRight: { key: 8, side: "bottom" },
  };

  const gameSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/game/" + gameName + "/"
  );

  gameSocket.onmessage = (e) => {
    clearCanvas();
    drawScene(JSON.parse(e.data));
  };

  gameSocket.onclose = (e) => {
    console.error("Game ws closed");
  };

  const keyStates = {};

  function keyPressed(ev) {
    const mapping = keyMappings[ev.key];
    if (mapping && !keyStates[ev.key]) {
      gameSocket.send(
        JSON.stringify({
          type: "key",
          key: mapping.key,
          player: playerName,
          side: mapping.side,
        })
      );
      keyStates[ev.key] = true;
    }
  }

  function keyReleased(ev) {
    const mapping = keyMappings[ev.key];
    if (mapping && keyStates[ev.key]) {
      gameSocket.send(
        JSON.stringify({
          type: "key",
          key: mapping.key,
          player: playerName,
          side: mapping.side,
        })
      );
      keyStates[ev.key] = false;
    }
  }

  document.addEventListener("keydown", keyPressed);
  document.addEventListener("keyup", keyReleased);

  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");

  function clearCanvas() {
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.fillStyle = "white";
  }

  function drawScene(scene) {
    scene.forEach((element) => {
      if (element.type === "score") {
        console.log(element.side + "'s score is " + element.score);
      } else {
        ctx.fillRect(
          ctx.canvas.width * element.x,
          ctx.canvas.height * element.y,
          ctx.canvas.width * element.width,
          ctx.canvas.height * element.height
        );
      }
    });
  }
}
