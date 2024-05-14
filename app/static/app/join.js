import { joinLobby } from "/static/app/game.js";
import { setBody } from "/static/app/index.js";

export function registerJoinForms() {
    document.querySelectorAll(".form-join").forEach((el) =>
        el.addEventListener("submit", async (ev) => {
            // prevent a page refresh
            ev.preventDefault();

            // register the join/create
            const formData = new URLSearchParams(
                [...el.elements].map((el) => [el.name, el.value])
            );
            const joinRes = await fetch(`/join?${formData}`, {
                method: "POST",
            });
            if (joinRes.status != 200) return alert(await joinRes.text());

            // switch to game view
            await setBody("/game");
            joinLobby(
                formData.get("lobby-name"),
                formData.get("player-1-name"),
                formData.get("player-2-name")
            );
        })
    );
}
