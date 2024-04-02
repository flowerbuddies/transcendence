import { join } from './game.js';

document.querySelectorAll('.form-join').forEach((el) =>
  el.addEventListener('submit', async (ev) => {
    ev.preventDefault(); // prevent a page refresh

    const formData = new FormData(ev.target);

    const res = await fetch('/join', {
      method: 'POST',
      body: formData,
    });

    if (res.status != 200) alert(await res.text());
    else join(formData.get('game-name'), formData.get('player-name'));
  })
);
