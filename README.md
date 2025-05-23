# 🏰 Fortress RPG Manager

**Fortress RPG Manager** es un bot de Discord temático inspirado en juegos de rol (RPG), que convierte la actividad de los usuarios en canales de voz en recursos para una fortaleza compartida. Ideal para comunidades roleras, servidores de D&D o simplemente para grupos que aman construir juntos.

---

## 🎮 Características principales

- ⏱️ **Generación de recursos en tiempo real**  
  Los usuarios conectados a canales de voz generan recursos como agua, comida, madera o piedra cada segundo.

- 🔥 **Rol "Descansado" en la fogata**  
  Quienes se conectan al canal `fogata` obtienen el rol "Descansado", que **duplica la generación de recursos** durante 30 minutos.

- 🧱 **Inicialización automática del servidor** (`/iniciar`)  
  Crea toda la infraestructura básica de canales y roles con un solo comando.

- 📦 **Comando `/ver_recursos`**  
  Muestra los recursos actuales almacenados en la base de datos en un embed estético.

- 🔄 **Panel de Recursos actualizado dinámicamente**  
  Muestra el estado actual de los recursos en canales de voz de solo lectura (por ejemplo: `💧 Agua (134)`).

---

🗃️ Base de datos
Este bot usa MySQL para persistencia. 

INSERT INTO fortress_resources (resource, amount) VALUES
('agua', 0), ('comida', 0), ('madera', 0), ('piedra', 0);

🛡️ Roles y canales automáticos
Al usar /iniciar, se crean las siguientes estructuras:

Categorías:

- Fogata
- Recolección
- Consejo (privado)
- Panel de Recursos (solo visualización)

Canales de voz (Recolección):
- recolectar agua
- recolectar comida
- recolectar piedra
- recolectar madera

Canales de estado (Panel de Recursos):

- 💧 Agua (X)
- 🍞 Comida (X)
- 🪓 Madera (X)
- 🪨 Piedra (X)

🌐 ¿Futuro despliegue?
El proyecto es compatible con Railway, Render o cualquier VPS con Python y acceso a MySQL.

📜 Licencia
Sin Licencia

Hecho con ❤️ por Akniz-RDG para fortalecer comunidades RPG.