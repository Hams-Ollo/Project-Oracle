import gradio as gr
from ..agents.orchestrator import Orchestrator

class ChatInterface:
    def __init__(self):
        self.orchestrator = Orchestrator()
        
    def create_interface(self):
        with gr.Blocks(css="style.css") as interface:
            gr.Markdown("# Multi-Agent Chat System")
            
            with gr.Row():
                with gr.Column():
                    chatbot = gr.Chatbot()
                    msg = gr.Textbox(label="Message")
                    submit = gr.Button("Send")
                
                with gr.Column():
                    agent_outputs = gr.JSON(label="Agent Responses")
            
            async def respond(message, history):
                responses = await self.orchestrator.route_message(message)
                
                # Combine responses for chatbot
                combined_response = "\n\n".join(
                    f"{agent}: {response}" 
                    for agent, response in responses.items()
                )
                
                history.append((message, combined_response))
                return history, responses
            
            submit.click(
                respond,
                inputs=[msg, chatbot],
                outputs=[chatbot, agent_outputs]
            )
            
        return interface 