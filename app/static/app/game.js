export function join(gameName, playerName) {
  document.getElementById("join-view").classList.add("d-none");
  document.getElementById("game-view").classList.remove("d-none");
  document.addEventListener("keydown", keyPressed);
  document.addEventListener("keyup", keyReleased);
  let canvas = document.getElementById("canvas");
  let ctx = canvas.getContext("2d");

  let sceneData = [];

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

  // render loop redraws the current scene and reports the time taken to backend
  const log_fps = false;
  let lastTimeStamp = 0;
  window.requestAnimationFrame(renderLoop);
  function renderLoop(timeStamp) {
    clearCanvas();
    drawScene(sceneData);
    if (gameSocket.readyState === WebSocket.OPEN) {
      gameSocket.send(
        JSON.stringify({
          type: "frame_time",
          time: timeStamp - lastTimeStamp,
        })
      );
      lastTimeStamp = timeStamp;
    }
    if (log_fps) {
      updateFPS();
    }
    window.requestAnimationFrame(renderLoop);
  }

  const gameSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/game/" + gameName + "/"
  );

  gameSocket.onmessage = (e) => {
    sceneData = JSON.parse(e.data);
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
