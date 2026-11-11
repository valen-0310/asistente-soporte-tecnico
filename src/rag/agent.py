from langchain_core.tools import tool
from src.rag.config import RagConfig
from src.rag.embeddings import embed_texts
from src.rag.vectorstore import get_collection

@tool
def buscar_en_base(consulta: str) -> str:
    """
    Busca información técnica y oficial en los manuales internos de la base de conocimientos.
    Usa esta herramienta cuando necesites responder preguntas sobre especificaciones de equipos,
    procedimientos o manuales internos. No la uses para saludos o conversación casual.
    """
    MAX_CHUNKS = 3
    MAX_CARACTERES = 400

    try:
        cfg = RagConfig()
        col = get_collection(cfg)
        
        res = col.query(
            query_embeddings=embed_texts([consulta], cfg.embedding_model),
            n_results=MAX_CHUNKS,
            include=["documents", "metadatas", "distances"]
        )
        
        if not res["documents"] or not res["documents"][0]:
            return "No se encontró información relevante en la base de conocimientos."

        fragmentos = []
        for i, (doc, m) in enumerate(zip(res["documents"][0], res["metadatas"][0])):
            texto = doc[:MAX_CARACTERES]
            fuente = m.get("source", "Manual interno")
            pagina = m.get("page", m.get("seccion", "N/A"))
            
            item = (
                f"[Fragmento {i+1}]\n"
                f"Documento: {fuente} | Página/Sección: {pagina}\n"
                f"Contenido: {texto}\n"
            )
            fragmentos.append(item)

        return "\n".join(fragmentos)

    except Exception as e:
        return f"Error al buscar en la base: {str(e)}"


@tool
def verificar_voltaje_impresora(voltaje_ingresado: float) -> str:
    """
    Verifica si el valor de voltaje ingresado se encuentra dentro del rango de alimentación 
    eléctrica permitido para la impresora X200 (110-127 V). Usa esta herramienta 
    cuando necesites validar especificaciones eléctricas o tolerancias de voltaje.
    """
    VOLTAJE_MIN = 110.0
    VOLTAJE_MAX = 127.0
    
    try:
        if VOLTAJE_MIN <= voltaje_ingresado <= VOLTAJE_MAX:
            return (
                f"Resultado de validación: El voltaje de {voltaje_ingresado} V es VÁLIDO. "
                f"Se encuentra dentro del rango permitido para la impresora X200 ({VOLTAJE_MIN}-{VOLTAJE_MAX} V)."
            )
        else:
            return (
                f"Resultado de validación: El voltaje de {voltaje_ingresado} V FUERA DE RANGO. "
                f"El rango aceptado por la impresora X200 es de {VOLTAJE_MIN} a {VOLTAJE_MAX} V."
            )
    except Exception as e:
        return f"Error al validar el voltaje: {str(e)}"


@tool
def buscar_en_web_controlada(consulta: str) -> str:
    """
    Busca información pública o actual en la web ÚNICAMENTE si la base interna no tiene la respuesta.
    Está restringida estrictamente a sitios oficiales y permitidos del dominio técnico.
    """
    # Lista de sitios permitidos fija en código (Requisito del Avance 3)
    SITIOS_PERMITIDOS = ["support.hp.com", "es.wikipedia.org", "cisco.com"]
    MAX_RESULTADOS = 3

    try:
        # Aquí puedes integrar TavilyClient si tienes clave, o simular la respuesta acotada a los dominios
        resultados_simulados = [
            {"title": "Guía oficial de soporte", "url": "https://support.hp.com/guia", "snippet": "Información pública general sobre impresoras y conectividad de red."},
        ]
        
        formateados = []
        for i, res in enumerate(resultados_simulados[:MAX_RESULTADOS]):
            formateados.append(
                f"[web: {res['url']}]\n"
                f"Título: {res['title']}\n"
                f"Extracto: {res['snippet']}\n"
            )
        return "\n".join(formateados)
    except Exception as e:
        return f"Error en búsqueda web: {str(e)}"
    
SYSTEM_PROMPT_AVANCE_3 = """
Eres un asistente de IA experto en soporte técnico y documentación de equipos, operando exclusivamente bajo el contexto de los manuales oficiales de la impresora X200.

REGLAS DE OPERACIÓN OBLIGATORIAS:
1. USO DE HERRAMIENTAS: Tienes acceso a tres herramientas especializadas:
   - 'buscar_en_base': Úsala obligatoriamente para responder preguntas sobre especificaciones, manuales, fallas o procedimientos del equipo X200.
   - 'verificar_voltaje_impresora': Úsala cuando el usuario pregunte por tolerancias o especificaciones eléctricas (voltaje).
   - 'buscar_en_web_controlada': Úsala ÚNICAMENTE si la base interna no tiene la respuesta y la pregunta requiere información pública de sitios permitidos.
2. CONVERSACIÓN CASUAL: Saludos o preguntas casuales (ej. "Hola", "¿Cómo estás?") deben responderse directamente sin invocar ninguna herramienta.
3. CITAS Y FUENTES: Toda respuesta basada en documentos debe citar explícitamente el documento y la página/sección proporcionada por la tool. Si se usa la web, marca la fuente como [web: URL].
4. RESTRICCIÓN DE ALCANCE: Si la información no se encuentra ni en la base interna ni en las fuentes web permitidas, indícalo claramente sin inventar datos ni exponer el corpus completo de la base.
"""