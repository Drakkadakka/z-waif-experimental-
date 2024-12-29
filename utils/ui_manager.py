from typing import Optional, Callable
import gradio as gr
import asyncio
import logging

class UIManager:
    def __init__(self, config):
        self.config = config
        self.current_stream_task: Optional[asyncio.Task] = None
        
    def create_interface(self):
        with gr.Blocks(theme=gr.themes.Default(
            primary_hue=self.config.ui.primary_color
        )) as interface:
            with gr.Row():
                txt_input = gr.Textbox(
                    placeholder="Type your message...",
                    show_label=False
                )
                btn_send = gr.Button("Send") if self.config.ui.enable_send_button else None
                
            with gr.Row():
                img_preview = gr.Image(
                    label="Visual Preview",
                    interactive=False
                )
                
            # Add hotkey handlers
            interface.load(self._setup_hotkeys)
            
            if btn_send:
                btn_send.click(
                    fn=self._handle_send,
                    inputs=[txt_input],
                    outputs=[img_preview]
                )
                
        return interface
        
    def _setup_hotkeys(self):
        try:
            # Setup hotkeys with error handling
            hotkeys = {
                self.config.hotkeys.send_message: self._handle_send,
                self.config.hotkeys.interrupt: self._handle_interrupt,
                self.config.hotkeys.reroll: self._handle_reroll,
            }
            return hotkeys
        except Exception as e:
            logging.warning(f"Failed to bind hotkeys: {e}")
            return {} 