param(
    [string]$cmd
)

switch ($cmd) {
    "up" {
        docker compose -f docker-compose.dev.yml up
    }
    "build" {
        docker compose -f docker-compose.dev.yml up --build
    }
    "down" {
        docker compose -f docker-compose.dev.yml down -v
    }
    "logs" {
        docker compose -f docker-compose.dev.yml logs -f
    }
    "restart" {
        docker compose -f docker-compose.dev.yml down
        docker compose -f docker-compose.dev.yml up
    }
    "soft_down"{
        docker compose -f docker-compose.dev.yml down
    }

    "re-build-backend"{
        docker compose -f docker-compose.dev.yml build backend
    }

    "psql"{
        docker exec -it postgres-dev psql -U postgres -d olimpiadas_bd_v2
    }
    default {
        Write-Host "Uso: ./dev.ps1 {up|build|down|logs|restart|soft_down|re-build-backend |psql}"
    }
}