# transcendence

## How to deploy with Docker Compose

1. Clone the repository using `git clone https://github.com/flowerbuddies/transcendence.git`
1. `cd transcendence`
1. Copy the `.env.example` into `.env`
1. Modify the `.env`-file values as necessary, the default values work for temporary environments
1. Run `docker compose up --build -d`
1. Navigate to https://localhost:8443 and enjoy! (Note: There is a warning generated due to a self-signed certificate)
1. To shut it down, run `docker compose down` in the project folder
