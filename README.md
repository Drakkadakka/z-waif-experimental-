# z-waif
Fully local &amp; open source AI Waifu. VTube Studio, Discord, Minecraft, custom made RAG (long term memory), alarm, and plenty more! Has a WebUI and hotkey shortcuts. All software is free (or extremely cheap)!

Requires Windows 10/11 and a CUDA (NVidia) GPU with atleast 12GB+ of video memory. 16GB is reccomended.
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

- 🍄 Vtuber Integration &nbsp; &nbsp; &emsp; &emsp; ღゝ◡╹ )ノ♡

	- Uses VTube Studio, and any compatible models!
 	- Ability to send emotes to the model, based on thier actions.
	- Idle / Speaking animation.
    - Twitch chat integration for live interaction!
    - Stream overlay support with customizable themes.

- 💾 Enhanced Memory &nbsp; &nbsp; &nbsp; &emsp; &emsp; (ー_ーゞ
	- Add Lorebook entries, for your waifu to remember a wide array of info as needed.
 	- Enable the custom RAG, giving your them knowledge of older conversations.
    - Import old logs and conversations, keeping your same AI waifu from another software!
    - Improved resource cleanup and memory management.

- 🎮 Modularity &emsp; &emsp; &emsp; &emsp; &emsp; &nbsp; &nbsp; ⌌⌈ ╹므╹⌉⌏
	- Enable various built in modules;
 		- Discord, for messaging.
		- Vision, to enable multimodal, and allow them to see!
   	 	- Alarm, so your waifu can wake you up in the morning.
     	- Minecraft, allowing your waifu to control the game using Baritone, Wurst, and other command based mods.
        - Twitch, for live streaming interaction and chat moderation.
	- All the options and modularity from any external software used. Oobabogoa, RVC Voice, ect.
    - Enhanced error handling and module initialization.

## YouTube Showcase

[![IMAGE ALT TEXT](http://img.youtube.com/vi/XBZL500hloU/0.jpg)](http://www.youtube.com/watch?v=XBZL500hloU "Z-Waif Showcase")[![IMAGE ALT TEXT](http://img.youtube.com/vi/IGMregWfhGI/0.jpg)](http://www.youtube.com/watch?v=IGMregWfhGI "Z-Waif Install")
If you need help / assistance, feel free to email me for this project at zwaif77@gmail.com

## Diaspora
#### The Original:
[TumblerWarren/Virtual_Avatar_ChatBot](https://github.com/TumblerWarren/Virtual_Avatar_ChatBot), this is the original project that this code is spun-off of. Full credit to that project - it provided the skeleton for the many advancements now in place.
#### Branches & Versions:
[SugarcaneDefender/z-waif]([https://github.com/Drakkadakka/z-waif-experimental-](https://github.com/SugarcaneDefender/z-waif)), OG; The original this is forked from all credit to them 

## Changelog

V1.4
- Fixed critical model initialization bug
  - Resolved issues with model not being properly defined in chat handler
  - Improved error handling for model generation
  - Added proper cleanup of resources

V1.3
- Added advanced Twitch integration
  - Full Twitch chat interaction support
  - Per-user memory system that maintains a year of interaction history
  - Personalized responses based on user chat history
  - Automatic memory cleanup for interactions older than 365 days
  - Memory persistence between bot restarts
  - Enhanced AI parameters for natural chat interaction

V1.2

- Lorebook messages are now directly infused into the encoding as it is sent.
	- This now sends all relevant lore triggered within the past 3 message sets, instead of just 1 with a required cooldown.
	- Lore triggering requirements were improved, to add plurals and fix edgecases.
	- You can still view what lore is triggered via the UI Logs.
- Random Memories will now trigger before the alarm.
	- This allows your bot to randomly scan your chat history, and remember past times.
	- You can also trigger random memories manually via the UI.

- Your VTuber can now look around, either Following Faces or Randomly.
	- This requires setting up 6 emotes for your VTuber. In order, they should have your VTuber's eyes doing the following (they can be named anything); 
		- "Look Slight Right"
		- "Look Right"
		- "Look Very Right"
		- "Look Slight Left"
		- "Look Left"
		- "Look Very Left"
	- In the .env, change "EYES_FOLLOW" to "Random" or "Faces". Set the "EYES_START_ID" to whatever emote slot the "Look Slight Right" is set up as.
		- Make sure all the eye looking emotes follow eachother in order. You can re-order them in VTube Studio if needed.
	- Obviously, you need a camera for the VTuber to follow faces, as well as the Vision module enabled.

- Other Roleplay Suppression is now disabled if you have "Cutoff at Newlines" off.
	- This will allow the bot to send messages containing character lines, such as "User:" or "Riley:".
	- This is to allow lists, info, and multi-user RP scenarios, if you want.
- Fixed issues with the RAG history desyncing when undoing messages.

---.---.---.---

v1.1-R2

- Fixed a few major bugs:
	- Fixed the "Error" taking over all of the Gradio WebUI
		- Happened due to Gradio & FastAPI dependency conflict (reminder: always vet your stuff~!)
	- Fixed issues with the software failing gently when you have no mic
	- Fixed crashes relating to searching for "Minecraft" logs, it now checks to see if the module is enabled first

---.---.---.---

v1.1

- Visual System
	- Toggleable as a module
	- Able to take new images or upload them directly for the AI to see
	- Runs using Ooba, like with the text
		- Can set the port to the existing, default one, or load another instance to dual wield
	- Option to see images before being sent
		- Can retake them
		- Use C/X on the keyboard to confirm
	- Automatically shrinks images to a proper size
- Fixed bits of the Minecraft module
	- Configurable "MinecraftUsername" to set your AI's name (stops feedback loops)
	- Configurable "MinecraftUsernameFollow" to set who your AI follows when doing "#follow"

---.---.---.---

V1.0

- Initial public release of Z-Waif. Contains:
	- WebUI
	- RAG
	- Discord
	- Semi-Minecraft Functionality
	- VTuber Emotes
	- Hotkeys
	- Various other initial release items

## Twitch Setup Instructions

To enable Twitch chat integration:

1. Create a Twitch Application:
   - Go to [Twitch Developer Console](https://dev.twitch.tv/console)
   - Create a new application
   - Set OAuth Redirect URL to `http://localhost:3000`
   - Save the Client ID

2. Generate Access Tokens:
   - Visit [Twitch Token Generator](https://twitchtokengenerator.com)
   - Select 'Bot Chat Token'
   - Grant required permissions (chat:read, chat:edit)
   - Save the Access Token and Refresh Token

3. Update your `.env` file with:
   ```
   TWITCH_TOKEN=your_access_token
   TWITCH_REFRESH_TOKEN=your_refresh_token
   TWITCH_CLIENT_ID=your_client_id
   TWITCH_CHANNEL=your_channel_name
   ```

4. Enable the Twitch module in settings

Your AI will now interact with Twitch chat, maintaining conversation history for each user for up to 365 days.

## Current To-Do

### 🎯 High Priority
- [ ] Multi-language support with automatic translation
- [ ] Plugin SDK for community-made modules
- [ ] Motion capture support for dynamic reactions
- [ ] Smart Home Integration module
  - [ ] Phillips Hue integration
  - [ ] Spotify/Music control
  - [ ] Temperature control

### 🧠 AI Enhancements
- [ ] Context-aware emotional responses
  - [ ] Voice tone matching
  - [ ] Dynamic expression mapping
- [ ] Emotional memory tracking system
- [ ] Cross-session learning implementation
- [ ] Custom personality templates
- [ ] Character relationship tracking

### 🎬 VTuber Features
- [ ] Collaborative streaming with multiple AI models
- [ ] Real-time background scene switching
- [ ] Custom animation trigger system
  - [ ] User-defined triggers
  - [ ] Event-based animations
- [ ] Scene composition tools
- [ ] Dynamic background environments

### 🛠️ Technical Improvements
- [ ] Memory categorization and priority system
- [ ] Custom memory pruning rules
- [ ] Performance optimization tools
- [ ] Debug mode for module testing
- [ ] Cross-module interaction system
- [ ] Batch conversation processing

### 📱 New Modules
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

### 💅 UI/UX Improvements
- [ ] Custom UI themes and layouts
- [ ] Voice pack management system
- [ ] Character appearance presets
- [ ] Custom reaction sets and emotes
- [ ] Conversation analytics dashboard
- [ ] Advanced prompt engineering interface

### 📊 Analytics & Export
- [ ] Conversation analytics and insights
- [ ] Export tools for content creation
- [ ] Performance metrics tracking
- [ ] Usage statistics dashboard

### 🧪 Experimental Features
- [ ] Multi-model conversation mixing
- [ ] Advanced context switching
- [ ] Dynamic personality evolution
- [ ] Real-time voice style transfer
