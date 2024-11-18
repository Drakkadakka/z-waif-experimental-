import random
import gradio as gr
import main
import API.Oogabooga_Api_Support
from utils.logging import debug_log, rag_log, kelvin_log, update_rag_log, clear_rag_log
import utils.settings
import utils.hotkeys
from utils.message_processing import process_input
from textblob import TextBlob  # Ensure TextBlob is installed

based_theme = gr.themes.Base(
    primary_hue="fuchsia",
    secondary_hue="indigo",
    neutral_hue="zinc",
)

with gr.Blocks(theme=based_theme, title="Z-Waif UI") as demo:
    #
    # CHAT
    #
    with gr.Tab("Chat"):
        #
        # Main Chatbox
        #
        chatbot = gr.Chatbot(height=540)
        msg = gr.Textbox(label="Your Message")

        def respond(message, chat_history):
            if message:
                # Process the message
                main.main_web_ui_chat(message)

                # Retrieve the result now
                message_reply = API.Oogabooga_Api_Support.receive_via_oogabooga()

                chat_history.append((message, message_reply))

                return "", chat_history  # Return empty string for msg and updated chat history

        def update_chat():
            # Return whole chat, plus the one I have just sent
            if API.Oogabooga_Api_Support.currently_sending_message != "":
                chat_combine = API.Oogabooga_Api_Support.ooga_history[-30:]
                chat_combine.append([API.Oogabooga_Api_Support.currently_sending_message, ""])
                return chat_combine[-30:]
            else:
                # Return whole chat, last 30
                return API.Oogabooga_Api_Support.ooga_history[-30:]

        # Ensure correct component instances are passed
        msg.submit(respond, inputs=[msg, chatbot], outputs=[msg, chatbot])  
        demo.load(update_chat, every=0.05, outputs=[chatbot])

        #
        # Basic Mic Chat
        #
        def recording_button_click():
            utils.hotkeys.speak_input_toggle_from_ui()
            return

        with gr.Row():
            recording_button = gr.Button(value="Mic (Toggle)")
            recording_button.click(fn=recording_button_click)
            recording_checkbox_view = gr.Checkbox(label="Now Recording!")

        #
        # Buttons
        #
        with gr.Row():
            def regenerate():
                main.main_web_ui_next()
                return

            def send_blank():
                print("\nSending blank message...\n")
                main.main_web_ui_chat("")
                return

            def undo():
                main.main_undo()
                return

            button_regen = gr.Button(value="Reroll")
            button_blank = gr.Button(value="Send Blank")
            button_undo = gr.Button(value="Undo")

            button_regen.click(fn=regenerate)
            button_blank.click(fn=send_blank)
            button_undo.click(fn=undo)

        #
        # Autochat Settings
        #
        def autochat_button_click():
            utils.hotkeys.input_toggle_autochat_from_ui()
            return

        def change_autochat_sensitivity(autochat_sens):
            utils.hotkeys.input_change_listener_sensitivity_from_ui(autochat_sens)
            return

        with gr.Row():
            autochat_button = gr.Button(value="Toggle Auto-Chat")
            autochat_button.click(fn=autochat_button_click)
            autochat_checkbox_view = gr.Checkbox(label="Auto-Chat Enabled")
            autochat_sensitivity_slider = gr.Slider(minimum=4, maximum=144, value=20, label="Auto-Chat Sensitivity")
            autochat_sensitivity_slider.change(fn=change_autochat_sensitivity, inputs=autochat_sensitivity_slider)

        #
        # Update Settings View
        #
        def update_settings_view():
            return utils.hotkeys.get_speak_input(), utils.hotkeys.get_autochat_toggle()

        demo.load(update_settings_view, every=0.05, outputs=[recording_checkbox_view, autochat_checkbox_view])

    #
    # DEBUG
    #
    with gr.Tab("Debug / Log"):
        debug_log_box = gr.Textbox(debug_log, lines=10, label="General Debug", autoscroll=True)
        rag_log_box = gr.Textbox(rag_log, lines=10, label="RAG Debug", autoscroll=True)
        kelvin_log_box = gr.Textbox(kelvin_log, lines=1, label="Random Temperature Readout")

        def update_logs():
            return debug_log, rag_log, kelvin_log

        demo.load(update_logs, every=0.05, outputs=[debug_log_box, rag_log_box, kelvin_log_box])

    #
    # LINKS
    #
    with gr.Tab("Links"):
        links_text = (
            "Github Project:\n" +
            "https://github.com/SugarcaneDefender/z-waif \n" +
            "\n" +
            "Documentation:\n" +
            "https://docs.google.com/document/d/1qzY09kcwfbZTaoJoQZDAWv282z88jeUCadivLnKDXCo/edit?usp=sharing \n" +
            "\n" +
            "YouTube:\n" +
            "https://www.youtube.com/@SugarcaneDefender \n" +
            "\n" +
            "Support more development on Ko-Fi:\n" +
            "https://ko-fi.com/zwaif \n" +
            "\n" +
            "Email me for premium AI-waifu development, install, and assistance:\n" +
            "zwaif77@gmail.com"
        )

        links_log = gr.Textbox(links_text, lines=14, label="Links")

def launch_demo():
    demo.launch(server_port=7864)

