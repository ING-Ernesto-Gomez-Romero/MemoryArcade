# Memory Arcade

Coleccion de dos minijuegos desarrollados con Python y Pygame: un memorama de
cartas y el clasico Snake. Todo el contenido visual se genera mediante codigo,
por lo que no se requieren imagenes, fuentes o sonidos externos.

## Caracteristicas

- Menu principal con navegacion por teclado y raton.
- Memorama con 16 cartas, contador de movimientos y cronometro.
- Snake con puntuacion, incremento gradual de velocidad y pausa.
- Pantallas de victoria, derrota y reinicio.
- Diseno adaptable dentro de una ventana de tamano fijo estable.
- Codigo organizado mediante clases y estados de juego.

## Tecnologias

- Python 3
- Pygame Community Edition (`pygame-ce`)

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

En macOS o Linux, activa el entorno con `source .venv/bin/activate`.
Se recomienda Python 3.11 o posterior.

## Controles

### Memorama

- Raton: seleccionar cartas.
- `Esc`: volver al menu.
- `R`: reiniciar la partida.

### Snake

- Flechas o `WASD`: mover.
- `P`: pausar.
- `Esc`: volver al menu.
- `R`: reiniciar despues de perder.

## Autor

Ernesto Gomez Romero  
[LinkedIn](https://www.linkedin.com/in/ernesto-g%C3%B3mez-romero-4398a541a/)
