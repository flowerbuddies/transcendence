export function join(gameName, playerName) {
  document.getElementById("join-view").classList.add("d-none");
  document.getElementById("game-view").classList.remove("d-none");

  // TODO: add support for 2 players on the same window
  const key1 = "q";
  const key2 = "a";

  const gameSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/game/" + gameName + "/"
  );

  gameSocket.onmessage = (e) => {
    // console.log(JSON.parse(e.data));
    clearCanvas();
    drawScene(JSON.parse(e.data));
  };

  gameSocket.onclose = (e) => {
    console.error("Game ws closed");
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
            side: "left",
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
            side: "left",
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
          side: "left",
        })
      );
      isKey1Pressed = false;
    } else if (ev.key === key2) {
      gameSocket.send(
        JSON.stringify({
          type: "key",
          key: 2,
          player: playerName,
          side: "left",
        })
      );
      isKey2Pressed = false;
    }
  }

  // we send the same event for both `keydown` and `keyup`
  // depending on the previous state, the server will be able to understand what's happening
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
      ctx.fillRect(
        ctx.canvas.width * element.x,
        ctx.canvas.height * element.y,
        ctx.canvas.width * element.width,
        ctx.canvas.height * element.height
      );
    });
  }
}
