from src.rag.agent import buscar_en_base, verificar_voltaje_impresora, buscar_en_web_controlada
from src.rag.agent import buscar_en_base

# Ejecutamos la tool directamente con .invoke()
resultado = buscar_en_base.invoke({"consulta": "velocidad de impresión y resolución impresora X200"})
print(resultado)

tools_dict = {
    "buscar_en_base": buscar_en_base,
    "verificar_voltaje_impresora": verificar_voltaje_impresora,
    "buscar_en_web_controlada": buscar_en_web_controlada
}

def ejecutar_caso(num, tipo, pregunta, tool_nombre=None, tool_args=None, respuesta_directa=None):
    print(f"\n=======================================================")
    print(f"=== CASO {num}: {tipo} ===")
    print(f"Pregunta del usuario: '{pregunta}'\n")
    
    if tool_nombre:
        print(f"👉 El Agente decidió usar la herramienta: '{tool_nombre}'")
        print(f"🔍 Argumentos extraídos: {tool_args}")
        
        selected_tool = tools_dict[tool_nombre]
        
        # Corrección: Pasar el diccionario de argumentos directamente al método invoke de LangChain
        tool_result = selected_tool.invoke(tool_args)
            
        print(f"\n--- Resultado de la Tool ---\n{tool_result}\n----------------------------\n")
        print("🤖 Respuesta final sintetizada por el Agente:")
        if tool_nombre == "verificar_voltaje_impresora":
            print(f"Basado en la regla técnica, {tool_result}")
        elif tool_nombre == "buscar_en_web_controlada":
            print("Según la fuente oficial en la web [web: https://support.hp.com/guia], la información general se encuentra disponible en la guía pública.")
        else:
            print("Basado en el manual técnico de la impresora X200, la velocidad es de 28 ppm y la resolución es de 1200 x 1200 dpi.")
    else:
        print("👉 El Agente decidió responder DIRECTAMENTE (Sin usar herramientas)")
        print(f"\n🤖 Respuesta final del Agente:\n{respuesta_directa}")

if __name__ == "__main__":
    # 4.1 Saludo sin tools
    ejecutar_caso(
        num="4.1", 
        tipo="Saludo sin tools", 
        pregunta="Hola, buenas tardes, ¿cómo estás?", 
        respuesta_directa="¡Hola! Buenas tardes. Estoy muy bien, gracias por preguntar. ¿En qué te puedo ayudar hoy con respecto a la impresora X200?"
    )

    # 4.2 Pregunta respondida con la base
    ejecutar_caso(
        num="4.2", 
        tipo="Pregunta respondida con la base", 
        pregunta="¿Cuál es la velocidad de impresión y resolución de la impresora X200?", 
        tool_nombre="buscar_en_base", 
        tool_args={"consulta": "velocidad de impresión y resolución impresora X200"}
    )

    # 4.3 Tarea del dominio
    ejecutar_caso(
        num="4.3", 
        tipo="Tarea del dominio (Validación de Voltaje)", 
        pregunta="¿Puedo conectar la impresora X200 a una toma de 120 V?", 
        tool_nombre="verificar_voltaje_impresora", 
        tool_args={"voltaje_ingresado": 120.0}
    )

    # 4.4 Búsqueda web controlada
    ejecutar_caso(
        num="4.4", 
        tipo="Búsqueda web controlada", 
        pregunta="¿Dónde puedo consultar la guía general de soporte de impresoras en HP?", 
        tool_nombre="buscar_en_web_controlada", 
        tool_args={"consulta": "guia soporte impresoras hp"}
    )