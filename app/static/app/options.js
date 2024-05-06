export function getPlayerCountsForType(type) {
    switch (type) {
        case "join.type.types.game1vAI":
            return [2];
        case "join.type.types.game1v1":
            return [2];
        case "join.type.types.tournament1v1":
            return [2, 4, 8, 16, 32, 64, 128, 256];
        case "join.type.types.game1v1v1v1":
            return [4];
        case "join.type.types.game1v1vAIvAI":
            return [4];
        case "join.type.types.tournament1v1v1v1":
            return [4, 16, 64, 256];
        default:
            return [42];
    }
}

export function updatePlayerOptions(select, allowedCounts) {
    select.options.length = 0;

    allowedCounts.forEach((count) => {
        const option = document.createElement("option");
        option.value = count;
        option.text = count;
        select.add(option);
    });
}

export function registerPlayerOptionsUpdate() {
    const typeSelect = document.getElementById("type-select");
    const playersSelect = document.getElementById("players-select");

    typeSelect.addEventListener("change", () => {
        const selectedType = typeSelect.value;
        const allowedPlayerCounts = getPlayerCountsForType(selectedType);
        updatePlayerOptions(playersSelect, allowedPlayerCounts);
    });

    typeSelect.dispatchEvent(new Event("change"));
}
