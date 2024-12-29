import random
import logging
from datetime import timedelta

import gradio
import gradio as gr
import main
import API.Oogabooga_Api_Support
import utils.logging
import utils.settings
import utils.hotkeys
import plotly.graph_objects as go
from utils.performance_metrics import get_system_metrics
from utils.personality_metrics import (
    get_personality_metrics,
    get_interaction_patterns,
    update_personality_weights,
    update_personality_config,
    PersonalityDimension
)
from utils.config import Config
from utils.error_boundary import ErrorBoundary

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@ErrorBoundary.system()
class VisualUI:
    def __init__(self):
        self.config = Config()
        self.config.load()
        self.preview_visible = False
        self.streaming = False
        
    def create_interface(self):
        with gr.Blocks(theme=gr.themes.Base(primary_hue=self.config.ui.primary_color)) as interface:
            with gr.Row():
                with gr.Column():
                    input_box = gr.Textbox(
                        placeholder="Type your message...",
                        show_label=False
                    )
                    with gr.Row():
                        send_btn = gr.Button(
                            "Send", 
                            variant="primary",
                            visible=self.config.ui.enable_send_button
                        )
                        reroll_btn = gr.Button("Reroll")
                        interrupt_btn = gr.Button("Stop")
                        
        return interface

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
        msg = gr.Textbox()

        def respond(message, chat_history):
            main.main_web_ui_chat(message)
            message_reply = API.Oogabooga_Api_Support.receive_via_oogabooga()
            chat_history.append((message, message_reply))
            return "", API.Oogabooga_Api_Support.ooga_history[-30:]

        def update_chat():
            if API.Oogabooga_Api_Support.currently_sending_message != "":
                chat_combine = API.Oogabooga_Api_Support.ooga_history[-30:]
                chat_combine.append([API.Oogabooga_Api_Support.currently_sending_message, ""])
                return chat_combine[-30:]
            else:
                return API.Oogabooga_Api_Support.ooga_history[-30:]

        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        demo.load(update_chat, every=1, outputs=[chatbot])

        #
        # Basic Mic Chat
        #

        def recording_button_click():

            utils.hotkeys.speak_input_toggle_from_ui()

            return


        with gradio.Row():

            recording_button = gr.Button(value="Mic (Toggle)")
            recording_button.click(fn=recording_button_click)

            recording_checkbox_view = gr.Checkbox(label="Now Recording!")



        #
        # Buttons
        #

        with gradio.Row():

            def regenerate():
                main.main_web_ui_next()
                return

            def send_blank():
                # Give us some feedback
                print("\nSending blank message...\n")

                # Send the blank
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


        with gradio.Row():

            autochat_button = gr.Button(value="Toggle Auto-Chat")
            autochat_button.click(fn=autochat_button_click)

            autochat_checkbox_view = gr.Checkbox(label="Auto-Chat Enabled")

            autochat_sensitivity_slider = gr.Slider(minimum=4, maximum=144, value=20, label="Auto-Chat Sensitivity")
            autochat_sensitivity_slider.change(fn=change_autochat_sensitivity, inputs=autochat_sensitivity_slider)



        def update_settings_view():
            return utils.hotkeys.get_speak_input(), utils.hotkeys.get_autochat_toggle()


        demo.load(update_settings_view, every=0.05,
                  outputs=[recording_checkbox_view, autochat_checkbox_view])

    #
    # PERFORMANCE METRICS
    #

    with gr.Tab("Performance Metrics"):
        with gr.Row():
            cpu_usage = gr.Label("CPU Usage: 0%")
            memory_usage = gr.Label("Memory Usage: 0%")

        def update_metrics():
            metrics = get_system_metrics()
            return (
                f"CPU Usage: {metrics['cpu'][-1]:.1f}%",
                f"Memory Usage: {metrics['memory'][-1]:.1f}%"
            )

        demo.load(update_metrics, every=2, outputs=[cpu_usage, memory_usage])

        # Performance Graph
        performance_plot = gr.Plot(label="System Performance")

        def update_plot():
            metrics = get_system_metrics()
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=metrics['time'],
                y=metrics['cpu'],
                name='CPU Usage (%)',
                mode='lines'
            ))
            
            fig.add_trace(go.Scatter(
                x=metrics['time'],
                y=metrics['memory'],
                name='Memory Usage (%)',
                mode='lines'
            ))
            
            fig.update_layout(
                title='System Performance',
                xaxis_title='Time',
                yaxis_title='Usage (%)',
                yaxis_range=[0, 100]
            )
            
            return fig

        demo.load(update_plot, every=10, outputs=[performance_plot])

    #
    # EMOTION METRICS
    #

    with gr.Tab("Emotion Metrics"):
        with gr.Row():
            current_emotion = gr.Label("Current Emotion: Neutral")
            emotion_intensity = gr.Label("Intensity: 0%")

        def update_emotion_metrics():
            if API.Oogabooga_Api_Support.currently_sending_message:
                emotion, intensity = API.Oogabooga_Api_Support.analyze_emotion(
                    API.Oogabooga_Api_Support.currently_sending_message
                )
                return (
                    f"Current Emotion: {emotion.title()}",
                    f"Intensity: {intensity*100:.1f}%"
                )
            return "Current Emotion: Neutral", "Intensity: 0%"

        demo.load(update_emotion_metrics, every=1, outputs=[current_emotion, emotion_intensity])

        # Emotion Graph
        emotion_plot = gr.Plot(label="Emotion Analysis")

        def update_emotion_plot():
            messages = API.Oogabooga_Api_Support.ooga_history[-10:]  # Last 10 messages
            emotions = []
            intensities = []
            times = list(range(len(messages)))
            
            for msg in messages:
                emotion, intensity = API.Oogabooga_Api_Support.analyze_emotion(msg[1])  # Analyze assistant responses
                emotions.append(emotion)
                intensities.append(intensity * 100)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times,
                y=intensities,
                name='Emotion Intensity',
                mode='lines',
                line=dict(color='fuchsia')
            ))
            
            fig.update_layout(
                title='Emotion Intensity Over Time',
                xaxis_title='Messages',
                yaxis_title='Intensity (%)',
                yaxis_range=[0, 100]
            )
            
            return fig

        demo.load(update_emotion_plot, every=5, outputs=[emotion_plot])

    #
    # VISUAL
    #

    if utils.settings.vision_enabled:
        with gr.Tab("Visual"):

            #
            # Take / Retake Image
            #

            with gr.Row():
                def take_image_button_click():
                    utils.hotkeys.view_image_from_ui()

                    return

                take_image_button = gr.Button(value="Take / Send Image")
                take_image_button.click(fn=take_image_button_click)


            #
            # Image Feed
            #

            with gr.Row():
                def cam_use_image_feed_button_click():
                    utils.settings.cam_use_image_feed = not utils.settings.cam_use_image_feed

                    return


                with gr.Row():
                    cam_use_image_feed_button = gr.Button(value="Check/Uncheck")
                    cam_use_image_feed_button.click(fn=cam_use_image_feed_button_click)

                    cam_use_image_feed_checkbox_view = gr.Checkbox(label="Use Image Feed (File Select)")


            #
            # Direct Talk
            #

            with gr.Row():
                def cam_direct_talk_button_click():
                    utils.settings.cam_direct_talk = not utils.settings.cam_direct_talk

                    return


                with gr.Row():
                    cam_direct_talk_button = gr.Button(value="Check/Uncheck")
                    cam_direct_talk_button.click(fn=cam_direct_talk_button_click)

                    cam_direct_talk_checkbox_view = gr.Checkbox(label="Direct Talk & Send")


            #
            # Reply After
            #

            with gr.Row():
                def cam_reply_after_button_click():
                    utils.settings.cam_reply_after = not utils.settings.cam_reply_after

                    return


                with gr.Row():
                    cam_reply_after_button = gr.Button(value="Check/Uncheck")
                    cam_reply_after_button.click(fn=cam_reply_after_button_click)

                    cam_reply_after_checkbox_view = gr.Checkbox(label="Post Reply / Reply After Image")



            #
            # Image Preview
            #

            with gr.Row():
                def cam_image_preview_button_click():
                    utils.settings.cam_image_preview = not utils.settings.cam_image_preview

                    return


                with gr.Row():
                    cam_image_preview_button = gr.Button(value="Check/Uncheck")
                    cam_image_preview_button.click(fn=cam_image_preview_button_click)

                    cam_image_preview_checkbox_view = gr.Checkbox(label="Preview before Sending")


            def update_visual_view():
                return utils.settings.cam_use_image_feed, utils.settings.cam_direct_talk, utils.settings.cam_reply_after, utils.settings.cam_image_preview


            demo.load(update_visual_view, every=0.05,
                      outputs=[cam_use_image_feed_checkbox_view, cam_direct_talk_checkbox_view, cam_reply_after_checkbox_view, cam_image_preview_checkbox_view])

    #
    # SETTINGS
    #


    with gr.Tab("Settings"):

        #
        # Hotkeys
        #

        def hotkey_button_click():
            utils.settings.hotkeys_locked = not utils.settings.hotkeys_locked

            return


        with gr.Row():
            hotkey_button = gr.Button(value="Check/Uncheck")
            hotkey_button.click(fn=hotkey_button_click)

            hotkey_checkbox_view = gr.Checkbox(label="Disable Keyboard Shortcuts (Input Toggle Lock)")


        #
        # Shadowchats
        #

        with gr.Row():
            def shadowchats_button_click():
                utils.settings.speak_shadowchats = not utils.settings.speak_shadowchats
                return

            shadowchats_button = gr.Button(value="Check/Uncheck")
            shadowchats_button.click(fn=shadowchats_button_click)

            shadowchats_checkbox_view = gr.Checkbox(label="Speak Typed Chats / Shadow Chats", value=utils.settings.speak_shadowchats)


        #
        # Soft Reset
        #

        with gr.Row():
            def soft_reset_button_click():
                API.Oogabooga_Api_Support.soft_reset()

                return

            soft_reset_button = gr.Button(value="Chat Soft Reset")
            soft_reset_button.click(fn=soft_reset_button_click)


        #
        # Random Memory
        #

        with gr.Row():
            def random_memory_button_click():
                main.main_memory_proc()

                return

            soft_reset_button = gr.Button(value="Proc a Random Memory")
            soft_reset_button.click(fn=random_memory_button_click)


        #
        # Shadowchats
        #

        with gr.Row():
            def newline_cut_button_click():
                utils.settings.newline_cut = not utils.settings.newline_cut

                return


            with gr.Row():
                newline_cut_button = gr.Button(value="Check/Uncheck")
                newline_cut_button.click(fn=newline_cut_button_click)

                newline_cut_checkbox_view = gr.Checkbox(label="Cutoff at Newlines (Double Enter)")


        #
        # Token Limit Slider
        #

        with gr.Row():

            def change_max_tokens(tokens_count):

                utils.settings.max_tokens = tokens_count
                return


            token_slider = gr.Slider(minimum=20, maximum=2048, value=utils.settings.max_tokens, label="Max Chat Tokens / Reply Length")
            token_slider.change(fn=change_max_tokens, inputs=token_slider)



        #
        # Alarm Time
        #

        def alarm_button_click(input_time):

            utils.settings.alarm_time = input_time

            print("\nAlarm time set as " + utils.settings.alarm_time + "\n")

            return


        with gr.Row():
            alarm_textbox = gr.Textbox(value=utils.settings.alarm_time, label="Alarm Time")

            alarm_button = gr.Button(value="Change Time")
            alarm_button.click(fn=alarm_button_click, inputs=alarm_textbox)


        #
        # Language Model Preset
        #

        def model_preset_button_click(input_text):

            utils.settings.model_preset = input_text

            print("\nChanged model preset to " + utils.settings.model_preset + "\n")

            return


        with gr.Row():
            model_preset_textbox = gr.Textbox(value=utils.settings.model_preset, label="Model Preset Name")

            model_preset_button = gr.Button(value="Change Model Preset")
            model_preset_button.click(fn=model_preset_button_click, inputs=model_preset_textbox)




        def update_settings_view():

            return utils.settings.hotkeys_locked, utils.settings.speak_shadowchats, utils.settings.newline_cut


        demo.load(update_settings_view, every=0.05, outputs=[hotkey_checkbox_view, shadowchats_checkbox_view, newline_cut_checkbox_view])

    #
    # PERSONALITY ADJUSTMENTS
    #

    with gr.Tab("Personality"):
        # Main Status Display
        with gr.Row():
            personality_status = gr.Label("Current Personality State")
            interaction_score = gr.Label("Interaction Score: 0")
            emotional_resonance = gr.Label("Emotional Resonance: 0")

        # Personality Dimension Sliders
        with gr.Column():
            with gr.Row():
                extraversion = gr.Slider(
                    minimum=-1, maximum=1, value=0, step=0.1,
                    label="Extraversion"
                )
                agreeableness = gr.Slider(
                    minimum=-1, maximum=1, value=0, step=0.1,
                    label="Agreeableness"
                )
            with gr.Row():
                conscientiousness = gr.Slider(
                    minimum=-1, maximum=1, value=0, step=0.1,
                    label="Conscientiousness"
                )
                openness = gr.Slider(
                    minimum=-1, maximum=1, value=0, step=0.1,
                    label="Openness"
                )
            with gr.Row():
                neuroticism = gr.Slider(
                    minimum=-1, maximum=1, value=0, step=0.1,
                    label="Neuroticism"
                )
                creativity = gr.Slider(
                    minimum=-1, maximum=1, value=0, step=0.1,
                    label="Creativity"
                )
            with gr.Row():
                empathy = gr.Slider(
                    minimum=-1, maximum=1, value=0, step=0.1,
                    label="Empathy"
                )
                assertiveness = gr.Slider(
                    minimum=-1, maximum=1, value=0, step=0.1,
                    label="Assertiveness"
                )

        # Advanced Settings
        with gr.Accordion("Advanced Settings", open=False):
            with gr.Row():
                adaptation_threshold = gr.Slider(
                    minimum=0, maximum=1, value=0.3, step=0.05,
                    label="Adaptation Threshold"
                )
                context_decay = gr.Slider(
                    minimum=0.5, maximum=1, value=0.95, step=0.01,
                    label="Context Decay Rate"
                )
            with gr.Row():
                emotional_memory_days = gr.Number(
                    value=7, label="Emotional Memory Span (days)"
                )
                personality_momentum = gr.Slider(
                    minimum=0, maximum=1, value=0.8, step=0.05,
                    label="Personality Shift Momentum"
                )

        # Visualization Tabs
        with gr.Tabs():
            # Personality Timeline
            with gr.Tab("Personality Evolution"):
                personality_plot = gr.Plot(label="Personality Dimensions Over Time")
            
            # Interaction Analysis
            with gr.Tab("Interaction Patterns"):
                with gr.Row():
                    interaction_plot = gr.Plot(label="Interaction History")
                    emotion_dist_plot = gr.Plot(label="Emotional Distribution")
            
            # Context Analysis
            with gr.Tab("Context Analysis"):
                with gr.Row():
                    context_plot = gr.Plot(label="Context Influence")
                    topic_coherence_plot = gr.Plot(label="Topic Coherence")

        def update_personality_view():
            metrics = get_personality_metrics()
            patterns = get_interaction_patterns()
            
            # Update status labels
            status = f"Profile: {metrics['dominant_trait']} | Depth: {patterns['depth_trend']:.2f}"
            score = f"Interaction Score: {metrics['interaction_score']:.2f}"
            resonance = f"Emotional Resonance: {patterns['emotional_connection']:.2f}"
            
            # Update dimension sliders
            sliders = [
                metrics[dim.value] for dim in PersonalityDimension
            ]
            
            # Create personality evolution plot
            fig1 = go.Figure()
            for dim in PersonalityDimension:
                fig1.add_trace(go.Scatter(
                    x=metrics['timestamps'],
                    y=metrics[dim.value + '_history'],
                    name=dim.value.title(),
                    mode='lines'
                ))
            
            # Create interaction pattern plots
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=patterns['timestamps'],
                y=patterns['interaction_scores'],
                name='Interaction Score',
                mode='lines',
                line=dict(color='fuchsia')
            ))
            
            # Create emotional distribution plot
            fig3 = go.Figure(data=[go.Pie(
                labels=list(patterns['emotion_distribution'].keys()),
                values=list(patterns['emotion_distribution'].values()),
                hole=.3
            )])
            
            # Create context influence plot
            fig4 = go.Figure()
            fig4.add_trace(go.Heatmap(
                z=patterns['context_influence'],
                x=list(PersonalityDimension.__members__.keys()),
                y=list(patterns['context_tags']),
                colorscale='Viridis'
            ))
            
            # Create topic coherence plot
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(
                x=patterns['timestamps'],
                y=patterns['topic_coherence'],
                name='Topic Coherence',
                mode='lines',
                line=dict(color='indigo')
            ))
            
            return (
                status, score, resonance,
                *sliders,
                fig1, fig2, fig3, fig4, fig5
            )

        def apply_personality_changes(*values):
            weights = {
                dim.value: value 
                for dim, value in zip(PersonalityDimension, values)
            }
            update_personality_weights(weights)
            return f"Updated personality weights: {', '.join(f'{k}={v:.2f}' for k,v in weights.items())}"

        def update_advanced_settings(threshold, decay, memory_days, momentum):
            update_personality_config({
                'adaptation_threshold': threshold,
                'context_decay_rate': decay,
                'emotional_memory_span': timedelta(days=memory_days),
                'personality_shift_momentum': momentum
            })
            return f"Updated configuration settings"

        # Update personality metrics every 5 seconds
        demo.load(
            update_personality_view,
            every=5,
            outputs=[
                personality_status,
                interaction_score,
                emotional_resonance,
                extraversion,
                agreeableness,
                conscientiousness,
                openness,
                neuroticism,
                creativity,
                empathy,
                assertiveness,
                personality_plot,
                interaction_plot,
                emotion_dist_plot,
                context_plot,
                topic_coherence_plot
            ]
        )

        # Apply slider changes
        all_sliders = [
            extraversion, agreeableness, conscientiousness,
            openness, neuroticism, creativity, empathy, assertiveness
        ]
        for slider in all_sliders:
            slider.change(
                fn=apply_personality_changes,
                inputs=all_sliders,
                outputs=gr.Textbox(label="Status")
            )

        # Apply advanced settings changes
        for setting in [adaptation_threshold, context_decay, 
                       emotional_memory_days, personality_momentum]:
            setting.change(
                fn=update_advanced_settings,
                inputs=[
                    adaptation_threshold,
                    context_decay,
                    emotional_memory_days,
                    personality_momentum
                ],
                outputs=gr.Textbox(label="Status")
            )

    #
    # DEBUG
    #

    with gr.Tab("Debug / Log"):
        debug_log = gr.Textbox(utils.logging.debug_log, lines=10, label="General Debug", autoscroll=True)
        rag_log = gr.Textbox(utils.logging.rag_log, lines=10, label="RAG Debug", autoscroll=True)
        kelvin_log = gr.Textbox(utils.logging.kelvin_log, lines=1, label="Random Temperature Readout")

        def update_logs():
            return utils.logging.debug_log, utils.logging.rag_log, utils.logging.kelvin_log

        demo.load(update_logs, every=0.05, outputs=[debug_log, rag_log, kelvin_log])



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
                      "zwaif77@gmail.com")

        rag_log = gr.Textbox(links_text, lines=14, label="Links")









def launch_demo():
    demo.launch(server_port=7864)


