####-----------IMPORTS------------###
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import mysql.connector
from datetime import datetime, timedelta

from config import TOKEN, DB_CONFIG

proximo_update = datetime.utcnow()

####-----------INTENTS Y CONFIG------------###
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

####-----------TAREA DE GENERACIÓN DE RECURSOS (1 segundo = 1 recurso)------------###
@tasks.loop(seconds=1)
async def generar_recursos():
    global proximo_update
    print("⏳ Loop ejecutado")

    try:
        guild = bot.guilds[0]
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        canales_recurso = {
            "recolectar agua": "agua",
            "recolectar comida": "comida",
            "recolectar madera": "madera",
            "recolectar piedra": "piedra"
        }

        for canal_nombre, recurso in canales_recurso.items():
            canal = discord.utils.get(guild.voice_channels, name=canal_nombre)
            if canal:
                for miembro in canal.members:
                    descansado = discord.utils.get(guild.roles, name="Descansado")
                    multiplicador = 2 if descansado in miembro.roles else 1

                    cursor.execute(
                        "UPDATE fortress_resources SET amount = amount + %s WHERE resource = %s",
                        (multiplicador, recurso)
                    )
                    print(f"⛏️ {miembro.display_name} generó {multiplicador} de {recurso}")

        # Actualización de nombres de canal cada 60 segundos
        if datetime.utcnow() >= proximo_update:
            cursor.execute("SELECT * FROM fortress_resources")
            recursos = dict(cursor.fetchall())
            panel = discord.utils.get(guild.categories, name="Panel de Recursos")
            if panel:
                for canal in panel.voice_channels:
                    nombre_base = canal.name.split("(")[0].strip()
                    clave = nombre_base.split(" ")[-1].lower()
                    if clave in recursos:
                        await canal.edit(name=f"{nombre_base} ({recursos[clave]})")
            proximo_update = datetime.utcnow() + timedelta(seconds=600)

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error en generación de recursos: {e}")

####-----------EVENTO READY------------###
@bot.event
async def on_ready():
    await tree.sync()
    generar_recursos.start()
    print(f"✅ Bot conectado como {bot.user}")

####-----------COMANDO /iniciar------------###
@tree.command(name="iniciar", description="Inicializa el servidor con las estructuras básicas")
async def iniciar(interaction: discord.Interaction):
    try:
        guild = interaction.guild
        owner = guild.owner

        if interaction.user != owner:
            await interaction.response.send_message(
                "❌ Solo el dueño del servidor puede ejecutar este comando.",
                ephemeral=True
            )
            return
# Crear categoría "Panel de Recursos"
        cat_panel = discord.utils.get(guild.categories, name="Panel de Recursos")
        if not cat_panel:
            cat_panel = await guild.create_category("Panel de Recursos")

        # Permisos: todos pueden ver, nadie puede conectarse
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True)
        }

        recursos = {
            "💧 Agua": "agua",
            "🍞 Comida": "comida",
            "🪓 Madera": "madera",
            "🪨 Piedra": "piedra"
        }

        for nombre, recurso in recursos.items():
            canal_existente = next((c for c in guild.voice_channels if c.name.startswith(nombre)), None)
            if not canal_existente:
                await guild.create_voice_channel(f"{nombre} (0)", category=cat_panel, overwrites=overwrites)

        await interaction.response.defer(thinking=True)

        # Verificar conexión a la base de datos y mostrar recursos
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fortress_resources")
            data = cursor.fetchall()
            print("📦 Recursos actuales desde la base de datos:")
            for resource, amount in data:
                print(f" - {resource.capitalize()}: {amount}")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"❌ Error al conectar con la base de datos: {e}")

        # ... aquí seguiría el resto de tu lógica de creación de canales y roles ...

        await interaction.followup.send("✅ ¡Servidor inicializado correctamente!")

    except discord.errors.NotFound:
        print("❌ Interacción no encontrada. Probablemente expiró antes del defer.")
    except Exception as e:
        print(f"❌ Error inesperado en /iniciar: {e}")

    await interaction.followup.send("✅ ¡Servidor inicializado correctamente!")

    

    # Crear roles
    descansado = discord.utils.get(guild.roles, name="Descansado")
    consejo = discord.utils.get(guild.roles, name="Consejo")
    if not descansado:
        descansado = await guild.create_role(name="Descansado")
    if not consejo:
        consejo = await guild.create_role(name="Consejo")

    # Crear categoría y canal Fogata
    cat_fogata = discord.utils.get(guild.categories, name="Fogata")
    if not cat_fogata:
        cat_fogata = await guild.create_category("Fogata")
    if not discord.utils.get(guild.voice_channels, name="fogata"):
        await guild.create_voice_channel("fogata", category=cat_fogata)

    # Crear categoría Recolección
    cat_recoleccion = discord.utils.get(guild.categories, name="Recolección")
    if not cat_recoleccion:
        cat_recoleccion = await guild.create_category("Recolección")

    recoleccion_canales = {
        "instrucciones-recolección": discord.ChannelType.text,
        "recolectar agua": discord.ChannelType.voice,
        "recolectar madera": discord.ChannelType.voice,
        "recolectar piedra": discord.ChannelType.voice,
        "recolectar comida": discord.ChannelType.voice,
    }

    for name, ch_type in recoleccion_canales.items():
        exists = discord.utils.get(guild.channels, name=name.lower())
        if not exists:
            if ch_type == discord.ChannelType.text:
                await guild.create_text_channel(name, category=cat_recoleccion)
            else:
                await guild.create_voice_channel(name, category=cat_recoleccion)

    # Crear categoría privada del Consejo
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        consejo: discord.PermissionOverwrite(view_channel=True)
    }

    cat_consejo = discord.utils.get(guild.categories, name="Consejo")
    if not cat_consejo:
        cat_consejo = await guild.create_category("Consejo", overwrites=overwrites)

    consejo_canales = {
        "instrucciones": discord.ChannelType.text,
        "menu de construcción": discord.ChannelType.text,
        "reunión": discord.ChannelType.voice
    }

    for name, ch_type in consejo_canales.items():
        exists = discord.utils.get(guild.channels, name=name.lower())
        if not exists:
            if ch_type == discord.ChannelType.text:
                await guild.create_text_channel(name, category=cat_consejo)
            else:
                await guild.create_voice_channel(name, category=cat_consejo)

    await interaction.followup.send("✅ ¡Servidor inicializado correctamente!")

###--- COMANDO VER RECURSOS---###
@tree.command(name="ver_recursos", description="Muestra los recursos almacenados en la base de datos")
async def ver_recursos(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fortress_resources")
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        # Formatea los datos
        descripcion = "\n".join([f"🪵 **{resource.capitalize()}**: `{amount}`" for resource, amount in data])

        embed = discord.Embed(
            title="📦 Recursos actuales de la fortaleza",
            description=descripcion,
            color=discord.Color.green()
        )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"❌ Error al consultar la base de datos: {e}")
        await interaction.followup.send("❌ Error al consultar los recursos.")

####----ROL DESCANSADO----#######
@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    fogata_channel = discord.utils.get(guild.voice_channels, name="fogata")
    descansado_role = discord.utils.get(guild.roles, name="Descansado")

    if not fogata_channel or not descansado_role:
        return

    # Usuario entra a fogata
    if after.channel == fogata_channel:
        print(f"🔥 {member.display_name} entró a Fogata. Esperando 5 minutos...")
        await asyncio.sleep(1)  # SEGUNDOS DE DEMORA MODIFICABLES (10 minutos  estandar)

        if member.voice and member.voice.channel == fogata_channel:
            await member.add_roles(descansado_role)
            print(f"✅ Rol 'Descansado' asignado a {member.display_name}")

            await asyncio.sleep(30)  # TIEMPO DE DURACIÓN de 30 minutos MODIFICABLE

            if descansado_role in member.roles:
                await member.remove_roles(descansado_role)
                print(f"⏳ Rol 'Descansado' quitado a {member.display_name}")


####-----------EJECUCIÓN DEL BOT------------###
bot.run(TOKEN)
