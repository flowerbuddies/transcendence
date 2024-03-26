const gameSocket = new WebSocket('ws://' + window.location.host + '/ws/game/');

gameSocket.onmessage = (e) => {
  const data = JSON.parse(e.data);
  document.querySelector('#chat-log').value += data.message + '\n';
};

gameSocket.onclose = (e) => {
  console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = (e) => {
  if (e.key === 'Enter') {
    // enter, return
    document.querySelector('#chat-message-submit').click();
  }
};

document.querySelector('#chat-message-submit').onclick = (e) => {
  const messageInputDom = document.querySelector('#chat-message-input');
  const message = messageInputDom.value;
  gameSocket.send(
    JSON.stringify({
      type: 'chat.message',
      message: message,
    })
  );
  messageInputDom.value = '';
};
