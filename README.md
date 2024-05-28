# transcendence

## How to deploy with Docker Compose

1. Clone the repository using `git clone https://github.com/flowerbuddies/transcendence.git`
1. `cd transcendence`
1. Copy the `.env.example` into `.env`
1. Fill the `.env`-file values as necessary
1. Run `docker compose up --build -d`
1. Navigate to https://localhost:8443 and enjoy! (Note: There is a warning generated due to a self-signed certificate)
1. To shut it down, run `docker compose down` in the project folder


## How to get basic information using the CLI

- Get the list of lobbies: `curl -k 'https://c2r5p9.hive.fi:8443' -H 'Accept: application/json'`
- Get information about a lobby using its name: `curl -k 'https://c2r5p9.hive.fi:8443/game?name=NAMEOFTHELOBBY' -H 'Accept: application/json'`
