Control software
====

Este directorio contiene el software de control del vehículo utilizado para la competencia. El código principal se encuentra en el archivo `src/main/main.ino` y está pensado para operar de forma autónoma mediante sensores de distancia y un giroscopio.

## Descripción general

El programa implementa un sistema de control distribuido en dos tareas concurrentes ejecutadas en distintos núcleos del microcontrolador:

- `getSensors`: lee continuamente los sensores de proximidad y el giroscopio, y actualiza los valores de navegación usados por la lógica de control.
- `control`: gestiona la dirección del vehículo y toma decisiones para evitar obstáculos detectados por los sensores.

## Hardware involucrado

El sketch está diseñado para trabajar con:

- 3 sensores ultrasónicos (izquierdo, centro y derecho)
- Un giroscopio BNO055
- Un servomotor para la dirección
- Un driver de motores y dos pines de control de movimiento
- Un botón de inicio

## Funcionamiento del sistema

1. Al encender el sistema, se inicializan los sensores y el servo.
2. El programa espera a que se presione el botón de inicio.
3. Una vez iniciado, el robot intenta avanzar mientras el sensor central no detecte un obstáculo.
4. Si el sensor central detecta un objeto dentro del rango configurado, el sistema inicia una maniobra de giro.
5. La dirección se ajusta según la lectura del giroscopio para mantener una trayectoria controlada.
6. El algoritmo usa los sensores laterales para decidir si girar en sentido horario o antihorario.

## Variables principales

- `dMin` y `dMax`: rangos de distancia usados para detectar obstáculos y decidir cuando girar.
- `MAX_TURN`: límite de giro del servo.
- `cw`: indica la dirección del giro actual.
- `turnOffset`: ayuda a mantener el ángulo de referencia durante la maniobra.

## Notas de implementación

- El código utiliza `FreeRTOS` mediante `xTaskCreatePinnedToCore` para ejecutar tareas en núcleos separados.
- La comunicación serial se usa para depurar y monitorear los valores de los sensores en tiempo real.
- El servo se controla con la librería `ServoEasing`.

## Archivos relevantes

- `src/main/main.ino`: archivo principal del firmware.
- `src/README.md`: documentación del software de control.
