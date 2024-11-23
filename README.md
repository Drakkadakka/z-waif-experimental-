# z-waif
Fully local & open source AI Waifu. VTube Studio, Discord, Minecraft, custom made RAG (long term memory), alarm, and plenty more! Has a WebUI and hotkey shortcuts. All software is free (or extremely cheap)!

Requires Windows 10/11 and a CUDA (NVidia) GPU with at least 12GB+ of video memory. 16GB is recommended.
Uses Oobabooga, RVC, and Whisper to run all AI systems locally. Works as a front end to tie many programs together into one cohesive whole.

The goal of the project is less about giving an "all in one package", and moreso to give you the tools and knowledge for you to create your own AI Waifu!

|<img src="https://i.imgur.com/3a5eGQK.png" alt="drawing" width="400"/> | <img src="https://i.imgur.com/BCE1snE.png" alt="drawing" width="400"/> |
|:---:|:---:|
|<img src="https://i.imgur.com/paMSUiy.jpeg" alt="drawing" width="400"/> | <img src="https://i.imgur.com/vXx1vXm.jpeg" alt="drawing" width="400"/> |

## Features

- 🎙️ Quality Conversation &nbsp; &emsp; &emsp; ( /・0・)

    - Speak back and forth, using Whisper text to speech.
    - Configure your own waifu's voice with thousands of possible models.
    - Imperial-tons of quality of life tweaks.
    - Enhanced model stability and resource management.
    - Context-aware emotional responses for more nuanced interactions.
    - Emotional memory tracking system to remember user sentiments.

- 🍄 Vtuber Integration &nbsp; &nbsp; &emsp; &emsp; ღゝ◡╹ )ノ♡
    - Uses VTube Studio, and any compatible models!
    - Ability to send emotes to the model, based on their actions.
    - Idle / Speaking animation.
    - Twitch chat integration for live interaction!
    - Stream overlay support with customizable themes.
    - Collaborative streaming with multiple AI models for enhanced interaction.
    - Real-time background scene switching and custom animation trigger system.

- 💾 Enhanced Memory &nbsp; &nbsp; &nbsp; &emsp; &emsp; (ー_ーゞ
    - Add Lorebook entries, for your waifu to remember a wide array of info as needed.
    - Enable the custom RAG, giving them knowledge of older conversations.
    - Import old logs and conversations, keeping your same AI waifu from another software!
    - Improved resource cleanup and memory management.
    - Memory categorization and priority system for better organization.
    - Custom memory pruning rules to manage memory effectively.

- 🎮 Modularity &emsp; &emsp; &emsp; &emsp; &emsp; &nbsp; &nbsp; ⌌⌈ ╹므╹⌉⌏
    - Enable various built-in modules;
        - Discord, for messaging.
        - Vision, to enable multimodal, and allow them to see!
        - Alarm, so your waifu can wake you up in the morning.
        - Minecraft, allowing your waifu to control the game using Baritone, Wurst, and other command-based mods.
        - Twitch, for live streaming interaction and chat moderation.
    - All the options and modularity from any external software used. Oobabogoa, RVC Voice, etc.
    - Enhanced error handling and module initialization.
    - Smart Home Integration module for controlling devices like Phillips Hue and Spotify.

- 📊 Analytics & Export
    - Conversation analytics and insights for better understanding interactions.
    - Export tools for content creation and performance metrics tracking.
    - Usage statistics dashboard for monitoring engagement.

- 🧪 Experimental Features
    - Multi-model conversation mixing for diverse interactions.
    - Dynamic personality evolution based on user interactions.
    - Real-time voice style transfer for varied vocal expressions.

## YouTube Showcase

[![IMAGE ALT TEXT](http://img.youtube.com/vi/XBZL500hloU/0.jpg)](http://www.youtube.com/watch?v=XBZL500hloU "Z-Waif Showcase")[![IMAGE ALT TEXT](http://img.youtube.com/vi/IGMregWfhGI/0.jpg)](http://www.youtube.com/watch?v=IGMregWfhGI "Z-Waif Install")

## Links
Here is [some documentation](https://docs.google.com/document/d/1qzY09kcwfbZTaoJoQZDAWv282z88jeUCadivLnKDXCo/edit?usp=sharing) that you can look at. It will show you how to install, how to use the program, and what options you have. Please also take a look at the Youtube videos linked above for installation.

Credit to [this other AI waifu project](https://github.com/TumblerWarren/Virtual_Avatar_ChatBot) for making the original base code/skeleton used here!

## Setup Instructions

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/z-waif.git
   cd z-waif
   ```

2. **Install Dependencies**:
   - Make sure you have Python 3.8 or higher installed.
   - Install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory and add your configuration settings, such as API keys and other necessary credentials.

4. **Run the Application**:
   - Start the application by running:
   ```bash
   python main.py
   ```

## SDK Plugin Setup

To set up and use the Plugin SDK, follow these steps:

1. **Create a Plugin Directory**:
   - Create a directory where you will store your custom plugins. For example, you can create a folder named `plugins` in the root of your project.

2. **Develop Your Plugin**:
   - Create a new Python file for your plugin inside the `plugins` directory. For example, `my_plugin.py`.
   - Ensure your plugin follows the required structure, including an `execute` method that will be called when the plugin is executed.

   ```python
   # Example of a simple plugin structure
   class MyPlugin:
       @staticmethod
       def execute(*args, **kwargs):
           print("MyPlugin executed with arguments:", args, kwargs)
   ```

3. **Load Your Plugin**:
   - Use the `load_plugins` method from the `Oogabooga_Api_Support` class to load your plugins from the specified directory. This can be done in your main application code.

   ```python
   Oogabooga_Api_Support.load_plugins('path/to/your/plugins')
   ```

4. **Enable Your Plugin**:
   - After loading, you can enable your plugin using the `enable_plugin` method.

   ```python
   Oogabooga_Api_Support.enable_plugin('my_plugin')
   ```

5. **Execute Your Plugin**:
   - You can execute your plugin using the `execute_plugin` method.

   ```python
   Oogabooga_Api_Support.execute_plugin('my_plugin', arg1, arg2, key1='value1')
   ```

6. **Check Plugin Status**:
   - Use the `list_plugins` method to see the status of your loaded plugins.

   ```python
   Oogabooga_Api_Support.list_plugins()
   ```

## Changelog
### V2.0
- Dynamic Expression Mapping
  - Expanded the `DynamicExpressionMapper` to include a wider range of expressions for more nuanced emotional representation.
  - Integrated dynamic expression mapping with VTube Studio to reflect emotions in real-time.

- VTube Studio Enhancements
  - Added support for setting expressions in VTube Studio based on detected emotions.
  - Improved integration with VTube Studio for real-time emotion-based expression changes.

- General Improvements
  - Enhanced modularity and error handling across various modules.
  - Improved memory management and resource cleanup processes.
  - Added new experimental features for multi-model conversation mixing and dynamic personality evolution.

- Custom Personality Templates
  - Implemented a system to create and manage custom personality templates.
  - Added methods to add, retrieve, and use personality templates in interactions.

- Complex Context-Aware Emotional Responses
  - Enhanced the emotional response generation to consider user context and previous messages.
  - Improved sentiment analysis for more nuanced interactions.

- Voice Tone Mapping
  - Implemented voice tone matching to enhance emotional responses based on audio analysis.

- Enhanced User Experience
  - Improved UI feedback for emotional responses and plugin actions.
  - Enhanced visual representation of emotional states during interactions.

- New Features
  - Introduced a feedback mechanism for users to provide input on AI responses, allowing for continuous improvement of the system.
  - Added support for additional platforms, enhancing the versatility of the AI assistant.
  - Implemented logging features for better tracking of interactions and system performance.

- Bug Fixes and Performance Improvements
  - Fixed various bugs related to memory management and emotional response generation.
  - Optimized performance for real-time emotion recognition and processing.

### V1.9
- Streamlined the codebase, removing unused and outdated sections of features

- Contextual Memory Implementation
  - Enhanced memory management to store and retrieve messages based on context.
  - Improved emotional memory tracking to remember user sentiments over time.

- Emotion Recognition Integration
  - Added advanced emotion recognition from text and audio inputs.
  - Implemented a method to analyze and recognize emotions for personalized interactions.
  - Integrated Whisper for audio transcription and emotion analysis.
  - Enhanced sentiment analysis for more nuanced interactions.

- Adaptive Learning Features
  - Introduced adaptive learning mechanisms to adjust based on user interactions.
  - Enhanced personalized response generation based on user profiles and past interactions.

- Dynamic Personality Shaping
  - Implemented dynamic personality adjustments based on user interactions.
  - Improved user profile management to tailor responses according to individual preferences.

- Dynamic Expression Mapping
  - Added dynamic expression mapping to associate user emotions with corresponding visual expressions.
  - Enhanced user interactions by appending expressions to responses based on detected emotions.

- Character Relationship Tracking
  - Implemented a system to track relationships between characters based on interactions.
  - Added methods to update and retrieve relationship data, including relationship scores and last interactions.
  - Enhanced character interactions by considering relationship dynamics in responses.

- Memory Cleanup
  - Implemented automatic cleanup of memories older than 365 days.
  - Enhanced memory management to ensure efficient storage and retrieval of user interactions.

- API Support Skeleton
  - Added a basic Flask API structure for interaction with the ChatLearner.
  - Implemented endpoints for learning messages, generating responses, and managing user profiles.

- Custom Personality Templates
  - Implemented a system to create and manage custom personality templates.
  - Added methods to add, retrieve, and use personality templates in interactions.

- Complex Context-Aware Emotional Responses
  - Enhanced the emotional response generation to consider user context and previous messages.
  - Improved sentiment analysis for more nuanced interactions.

- Voice Tone Mapping
  - Implemented voice tone matching to enhance emotional responses based on audio analysis.

- Enhanced User Experience
  - Improved UI feedback for emotional responses and plugin actions.
  - Enhanced visual representation of emotional states during interactions.

- Various Bug Fixes and Performance Improvements
  - Fixed various bugs related to memory management and emotional response generation.
  - Optimized performance for real-time emotion recognition and processing.

### V1.8
- Cross-Session Learning Implementation
  - Added functionality to learn from messages across different sessions.
  - Introduced a method to retrieve learned messages and sentiments from the database.

- Custom Personality Templates
  - Implemented a system to create and manage custom personality templates.
  - Added methods to add, retrieve, and use personality templates in interactions.

- Complex Context-Aware Emotional Responses
  - Enhanced the emotional response generation to consider user context and previous messages.
  - Improved sentiment analysis for more nuanced interactions.

- Voice Tone Mapping
  - Implemented voice tone matching to enhance emotional responses based on audio analysis.

### V1.7
- Complex Context-Aware Emotional Responses
  - Enhanced the emotional response generation to consider user context and previous messages.
  - Improved sentiment analysis for more nuanced interactions.

- Plugin SDK Enhancements
  - Added support for complex plugins that can utilize the new emotional response features.
  - Improved documentation for plugin development.

- Memory Management Improvements
  - Further optimized memory cleanup processes.
  - Enhanced memory persistence options for loaded plugins.

- User Interface Updates
  - Improved UI feedback for emotional responses and plugin actions.
  - Enhanced visual representation of loaded plugins and their statuses.

### V1.6
- Plugin SDK Integration
  - Introduced support for community-made modules via a Plugin SDK.
  - Dynamic loading of plugins from specified directories.
  - Enhanced error handling during plugin loading and execution.
  - Added methods for listing, enabling, and disabling plugins.
  - Improved resource management for loaded plugins.

- Enhanced Memory Management
  - Implemented a more robust memory cleanup process.
  - Added configuration options for memory persistence and cleanup frequency.

- Improved Error Handling
  - Enhanced error handling across various modules, including Discord and Twitch integrations.
  - Added detailed logging for plugin execution errors.

- User Interface Improvements
  - Updated UI to better display loaded plugins and their statuses.
  - Enhanced visual feedback for plugin actions and errors.

### V1.5
- Enhanced Discord Integration
  - Added comprehensive voice channel support:
    - Text-to-speech (TTS) command for voice output.
    - Audio playback from URLs.
    - Voice recording and transcription.
    - Improved voice channel management.
  - New Discord Commands:
    - /tts - Convert text to speech in voice channels.
    - /play - Play audio from URLs.
    - /stop - Stop current audio playback.
    - /help - Detailed command list.
  - Enhanced error handling for voice features.
  - Improved voice connection stability.
  - Better resource management for audio streams.
  - Prevented downloading of entire playlists when a single video URL is provided.

### V1.4
- Fixed critical model initialization bug:
  - Resolved issues with the model not being properly defined in chat handler.
  - Improved error handling for model generation.
  - Added proper cleanup of resources.

### V1.3
- Added advanced Twitch integration:
  - Full Twitch chat interaction support.
  - Per-user memory system that maintains a year of interaction history.
  - Personalized responses based on user chat history.
  - Automatic memory cleanup for interactions older than 365 days.
  - Memory persistence between bot restarts.
  - Enhanced AI parameters for natural chat interaction.

### V1.2
- Lorebook messages are now directly infused into the encoding as it is sent:
  - This now sends all relevant lore triggered within the past 3 message sets, instead of just 1 with a required cooldown.
  - Lore triggering requirements were improved to add plurals and fix edge cases.
  - You can still view what lore is triggered via the UI Logs.
- Random Memories will now trigger before the alarm:
  - This allows your bot to randomly scan your chat history and remember past times.
  - You can also trigger random memories manually via the UI.

- Your VTuber can now look around, either following faces or randomly:
  - This requires setting up 6 emotes for your VTuber. In order, they should have your VTuber's eyes doing the following (they can be named anything):
    - "Look Slight Right"
    - "Look Right"
    - "Look Very Right"
    - "Look Slight Left"
    - "Look Left"
    - "Look Very Left"
  - In the .env, change "EYES_FOLLOW" to "Random" or "Faces". Set the "EYES_START_ID" to whatever emote slot the "Look Slight Right" is set up as.
    - Make sure all the eye looking emotes follow each other in order. You can re-order them in VTube Studio if needed.
  - Obviously, you need a camera for the VTuber to follow faces, as well as the Vision module enabled.

- Other Roleplay Suppression is now disabled if you have "Cutoff at Newlines" off:
  - This will allow the bot to send messages containing character lines, such as "User:" or "Riley:".
  - This is to allow lists, info, and multi-user RP scenarios, if you want.
- Fixed issues with the RAG history desyncing when undoing messages.

---.---.---.---

v1.1-R2

- Fixed a few major bugs:
  - Fixed the "Error" taking over all of the Gradio WebUI:
    - Happened due to Gradio & FastAPI dependency conflict (reminder: always vet your stuff~!)
  - Fixed issues with the software failing gently when you have no mic.
  - Fixed crashes relating to searching for "Minecraft" logs; it now checks to see if the module is enabled first.

---.---.---.---

v1.1

- Visual System:
  - Toggleable as a module.
  - Able to take new images or upload them directly for the AI to see.
  - Runs using Ooba, like with the text:
    - Can set the port to the existing, default one, or load another instance to dual wield.
  - Option to see images before being sent:
    - Can retake them.
    - Use C/X on the keyboard to confirm.
  - Automatically shrinks images to a proper size.
- Fixed bits of the Minecraft module:
  - Configurable "MinecraftUsername" to set your AI's name (stops feedback loops).
  - Configurable "MinecraftUsernameFollow" to set who your AI follows when doing "#follow".

---.---.---.---

V1.0

- Initial public release of Z-Waif. Contains:
  - WebUI.
  - RAG.
  - Discord.
  - Semi-Minecraft Functionality.
  - VTuber Emotes.
  - Hotkeys.
  - Various other initial release items.

## Current To-Do

### High Priority
- [ ] Multi-language support with automatic translation
- [ ] Motion capture support for dynamic reactions
- [ ] Smart Home Integration module
  - [ ] Phillips Hue integration
  - [ ] Spotify/Music control
  - [ ] Temperature control
  - [ ] Documentation for plugin development
  - [ ] Example plugins for community reference
- [ ] Fix talking output in Discord

### AI Enhancements
- [ ] Implement advanced emotion recognition for improved interaction
- [ ] Develop adaptive learning mechanisms to adjust responses based on user interactions
- [ ] Enhance personalized response generation based on user profiles and past interactions
- [ ] Introduce dynamic personality adjustments based on user interactions
- [ ] Improve contextual memory management to store and retrieve messages based on context
- [ ] Implement complex context-aware emotional responses for more nuanced interactions
- [ ] Enhance sentiment analysis for better understanding of user emotions
- [ ] Integrate voice tone mapping to enhance emotional responses based on audio analysis

### VTuber Features
- [ ] Collaborative streaming with multiple AI models
- [ ] Real-time background scene switching
- [ ] Custom animation trigger system
  - [ ] User-defined triggers
  - [ ] Event-based animations
- [ ] Scene composition tools
- [ ] Dynamic background environments

### Technical Improvements
- [ ] Memory categorization and priority system
- [ ] Custom memory pruning rules
- [ ] Performance optimization tools
- [ ] Debug mode for module testing
- [ ] Cross-module interaction system
- [ ] Batch conversation processing

### New Modules
- [ ] Calendar Sync
  - [ ] Google Calendar integration
  - [ ] Outlook support
- [ ] Weather Integration
- [ ] Browser Extension
  - [ ] Chrome/Firefox support
  - [ ] Web browsing assistance
- [ ] Music Player Control
  - [ ] Mood-based playlists
  - [ ] Voice commands

### UI/UX Improvements
- [ ] Custom UI themes and layouts
- [ ] Voice pack management system
- [ ] Character appearance presets
- [ ] Custom reaction sets and emotes
- [ ] Conversation analytics dashboard
- [ ] Advanced prompt engineering interface

### Analytics & Export
- [ ] Conversation analytics and insights
- [ ] Export tools for content creation
- [ ] Performance metrics tracking
- [ ] Usage statistics dashboard

### Experimental Features
- [ ] Multi-model conversation mixing
- [ ] Advanced context switching
- [ ] Dynamic personality evolution
- [ ] Real-time voice style transfer
