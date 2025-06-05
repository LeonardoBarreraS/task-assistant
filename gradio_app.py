import gradio as gr
import asyncio
import os
from langgraph_sdk import get_client
from langchain_core.messages import HumanMessage

class TaskMaistroInterface:
    def __init__(self):
        # Railway inyectará esta URL automáticamente
        api_url = os.environ.get("LANGGRAPH_API_URL", "http://localhost:8123")
        self.client = get_client(url=api_url)
        self.graph_name = "task_maistro"
        self.thread_id = None
        
    async def get_or_create_thread(self):
        """Obtiene o crea un thread único para la sesión"""
        if self.thread_id is None:
            thread = await self.client.threads.create()
            self.thread_id = thread["thread_id"]
        return self.thread_id
        
    async def chat_with_agent(self, message: str):
        """Chat principal con el agente Task Maistro"""
        try:
            # Obtener o crear thread para esta sesión
            thread_id = await self.get_or_create_thread()
            
            # Configuración fija - siempre el mismo usuario
            config = {
                "configurable": {
                    "user_id": "default_user",
                    "todo_category": "general",
                    "task_maistro_role": "You are Task Maistro, a helpful AI assistant that helps users manage their tasks and todos."
                }
            }
            
            # Stream la respuesta del agente
            response_text = ""
            async for chunk in self.client.runs.stream(
                thread_id,
                self.graph_name,
                input={"messages": [HumanMessage(content=message)]},
                config=config,
                stream_mode="messages"
            ):
                if chunk.event == "messages" and chunk.data:
                    for message_chunk in chunk.data:
                        if hasattr(message_chunk, 'content') and message_chunk.content:
                            response_text += message_chunk.content
            
            return response_text or "I received your message but couldn't generate a response."
            
        except Exception as e:
            return f"Error connecting to Task Maistro: {str(e)}"

# Inicializar la interfaz
task_interface = TaskMaistroInterface()

# Wrapper síncrono para Gradio
def chat_wrapper(message, history):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(
            task_interface.chat_with_agent(message)
        )

        # Asegurar que response sea siempre string
        if not isinstance(response, str):
            response = str(response)
        if history is None:
            history = []   

        history.append([message, response])
        return history, ""
    finally:
        loop.close()

# Crear la interfaz Gradio
with gr.Blocks(
    title="Task Maistro - AI Task Manager",
    theme=gr.themes.Soft()
) as demo:
    
    gr.Markdown("# 🤖 Task Maistro")
    gr.Markdown("Your AI assistant for managing tasks and todos.")
    
    # Chat interface
    chatbot = gr.Chatbot(
        height=600,
        show_label=False,
        
    )
    
    # Input row
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Type your message here...",
            container=False,
            scale=4,
            show_label=False
        )
        send_btn = gr.Button("Send", variant="primary", scale=1)
    
    # Event handlers
    send_btn.click(
        chat_wrapper,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    )
    
    msg.submit(
        chat_wrapper,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    )

if __name__ == "__main__":
    print("Starting Task Maistro Gradio Interface...")
    print(f"Port: {os.environ.get('PORT', 8080)}")
    print(f"API URL: {os.environ.get('LANGGRAPH_API_URL', 'Not set')}")
    
    # Configuración Railway-específica
    port = int(os.environ.get("PORT", 8080))
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=True,
        show_error=True,
    )