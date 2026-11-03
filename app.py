import streamlit as st
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Configuración
ENDPOINT = "https://foundry-tecnun-resource.services.ai.azure.com/api/projects/foundry-tecnun-project"
AGENT_NAME = "agent-felipe"

st.set_page_config(page_title=f"Chat - {AGENT_NAME}", page_icon="🤖")
st.title(f"Chat con {AGENT_NAME} 🤖")

# 1. Caché para la conexión de Azure (evita re-autenticarse en cada click)
@st.cache_resource
def init_clients():
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(
        endpoint=ENDPOINT,
        credential=credential,
        allow_preview=True,
    )
    openai_client = project_client.get_openai_client(agent_name=AGENT_NAME)
    return openai_client

try:
    openai_client = init_clients()
except Exception as e:
    st.error(f"Error de autenticación con Azure: {e}")
    st.stop()

# 2. Inicializar el estado de la sesión (memoria de la página)
if "conversation_id" not in st.session_state:
    # Creamos un hilo de conversación único para esta sesión de navegador
    conversation = openai_client.conversations.create()
    st.session_state.conversation_id = conversation.id

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Mostrar el historial de mensajes en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Caja de texto para el usuario
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    
    # Guardar y mostrar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Llamar al agente y mostrar la respuesta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                response = openai_client.responses.create(
                    conversation=st.session_state.conversation_id,
                    input=[{"role": "user", "content": prompt}],
                )
                
                respuesta_agente = response.output_text
                st.markdown(respuesta_agente)
                
                # Guardar la respuesta en el historial
                st.session_state.messages.append({"role": "assistant", "content": respuesta_agente})
                
            except Exception as e:
                st.error(f"Error de comunicación con el agente: {e}")