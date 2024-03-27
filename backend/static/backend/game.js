// args
const key1 = 'q';
const key2 = 'a';
const player = 'elie';

const gameSocket = new WebSocket('ws://' + window.location.host + '/ws/game/');

gameSocket.onmessage = (e) => {
  document.getElementById('logs').value += e.data + '\n';
};

gameSocket.onclose = (e) => {
  console.error('Game ws closed');
};

let isKey1Pressed = false;
let isKey2Pressed = false;

function keyPressed(ev) {
  if (ev.key === key1) {
    if (!isKey1Pressed)
      gameSocket.send(
        JSON.stringify({
          type: 'key',
          key: 1,
          player: player,
        })
      );
    isKey1Pressed = true;
  } else if (ev.key === key2) {
    if (!isKey2Pressed)
      gameSocket.send(
        JSON.stringify({
          type: 'key',
          key: 2,
          player: player,
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
        player: player,
      })
    );
    isKey1Pressed = false;
  } else if (ev.key === key2) {
    gameSocket.send(
      JSON.stringify({
        type: 'key',
        key: 2,
        player: player,
      })
    );
    isKey2Pressed = false;
  }
}

document.addEventListener('keydown', keyPressed);
document.addEventListener('keyup', keyReleased);
