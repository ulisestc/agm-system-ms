# 📑 Contratos gRPC (Protocol Buffers)

Este directorio es el núcleo de la comunicación del sistema **AGM-Systems**. Aquí se definen los contratos que rigen cómo interactúan los microservicios entre sí, asegurando que todos hablen el mismo "idioma".

### ¿Por qué usamos gRPC y Protobuf?
- **Tipado Fuerte:** A diferencia de las APIs REST tradicionales basadas en JSON, Protobuf define esquemas estrictos. Esto garantiza que un microservicio no envíe datos que otro no pueda procesar, eliminando errores de comunicación comunes.
- **Alto Rendimiento:** Los mensajes se serializan en un formato binario extremadamente compacto, lo que reduce drásticamente la latencia y el consumo de ancho de banda en comparación con el texto plano.
- **Contratos como Código:** Estos archivos funcionan como la "Fuente de Verdad". A partir de ellos, se genera automáticamente el código de los clientes y servidores, asegurando que la implementación siempre coincida con la definición del contrato.

### Organización
- Cada microservicio tiene su propio archivo `.proto` que describe sus capacidades (métodos) y las estructuras de datos que intercambia (mensajes).
