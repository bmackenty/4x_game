# 4X Galactic Empire Management Game

A simple text-based 4X strategy game set in a futuristic space-faring civilization. Manage your galactic empire through manufacturing, trading, exploration, and conquest.

## Game Features

- **Character Creation**: 6 unique character classes with different starting bonuses and backgrounds
- **Ship Building**: Custom ship construction system with hull types, engines, weapons, shields, and special systems
- **Space Navigation**: 3D galaxy with 30-40 star systems to explore using X,Y,Z coordinates
- **Manufacturing Platforms**: 20+ unique industrial facilities from Solar Forge Arrays to Temporal Forges
- **Commodities Trading**: Extensive catalog of exotic goods, bio-materials, and raw resources
- **Ship Classes**: Various starship types from stealth frigates to massive freighters
- **Space Stations**: Purchase and manage orbital installations throughout the galaxy
- **Ship Upgrades**: Enhance your vessels with advanced components and systems
- **Dynamic Economy**: Advanced supply/demand system with market fluctuations, production cycles, and economic events
- **Galactic Events**: Dynamic event system generating random occurrences that affect markets, travel, and politics
- **News System**: Comprehensive galactic news feed with breaking news, categorized reports, and travel advisories
- **Political Scandals**: Humorous PG-13 to R-rated political scandal events that affect faction relations

## How to Play

### Quick Start
1. **Recommended**: Modern Interface with mouse support:
   ```bash
   ./run_ui.sh
   ```
   
2. **Alternative**: Terminal-only interface:
   ```bash
   python3 game.py
   ```

2. Create your commander profile and choose a character class and background
3. Start with credits based on your character class (8k-15k)
4. Use the main menu to:
   - Browse available assets and commodities
   - Trade goods for profit
   - Purchase ships, stations, and manufacturing platforms
   - Build custom ships with the ship builder
   - View your character profile and stats
   - Build your galactic empire!

### Game Mechanics

**Starting Resources:**
- 8,000-15,000 credits (depends on character class)
- Basic Transport (starter ship) + character-specific ships/stations/platforms
- Empty inventory
- Unique character stats and abilities

**Main Activities:**
1. **Character Creation** - Choose from 6 classes (Merchant, Explorer, Industrial Magnate, Military Commander, Diplomat, Scientist) and 6 backgrounds
2. **Browse Catalogs** - Learn about available ships, stations, platforms, and goods
3. **Trade Commodities** - Buy low, sell high to increase your credits
4. **Purchase Assets** - Invest in ships (50k-150k), stations (500k), or platforms (250k)
5. **Ship Builder** - Design custom ships with different hull types, engines, weapons, shields, and special systems
6. **Navigate Space** - Pilot ships through 3D galaxy, visit star systems, manage fuel and cargo
7. **Trade Economics** - Buy/sell commodities with dynamic supply/demand pricing across different markets
8. **Ship Upgrades** - Enhance ships with better engines, cargo systems, and defensive upgrades
9. **Station Management** - Purchase, upgrade, and collect income from space stations
10. **Manage Empire** - View your growing collection of assets and inventory
11. **Galactic News & Events** - Stay informed about current events, scandals, and market conditions

**Pricing:**
- Commodities: 5 credits each (base price)
- Ships: 50,000 - 150,000 credits (varies by class)
- Custom Ships: 38,000 - 182,000+ credits (depends on components)
- Space Stations: 500,000 credits each
- Manufacturing Platforms: 250,000 credits each

## Character Classes

All characters start with a **Basic Transport** (starter ship) plus class-specific bonuses:

**Merchant Captain**: Trade specialist with bonus credits and Aurora-Class Freighter
**Explorer**: Frontier scout with exploration bonuses and Stellar Voyager
**Industrial Magnate**: Manufacturing expert with production bonuses and Nanoforge Spires platform
**Military Commander**: Combat veteran with tactical advantages and Aurora Ascendant cruiser
**Diplomat**: Negotiation specialist with communication advantages and Celestium-Class Communication Ship
**Scientist**: Research focused with technology bonuses, Nebula Drifter ship, and Archive of Echoes station

## Ship Building

Design custom ships by selecting:
- **Hull Types**: Light (fast), Standard (balanced), Heavy (tough), Mega (massive)
- **Engines**: Ion Drive, Fusion Engine, Ether Drive, Quantum Jump Drive
- **Weapons**: Pulse Cannons, Plasma Torpedoes, Etheric Disruptors, Gravity Cannon
- **Shields**: Basic Deflectors, Plasma Shields, Etheric Barriers, Phase Shields
- **Special Systems**: Cargo Expander, Stealth Generator, Scanner Array, Mining Laser, Research Lab, Medical Bay

Or use pre-built templates: Scout Ship, Merchant Vessel, Warship, Explorer, Miner

## Space Navigation

Explore a 3D galaxy (100x100x50 coordinates) containing 30-40 unique star systems:

### Flight Mechanics
- **3D Coordinates**: Navigate using X, Y, Z positioning (0-100, 0-100, 0-50)
- **Fuel System**: Ships consume 2 fuel per distance unit traveled
- **Jump Range**: Each ship has a maximum jump distance (15-25 units)
- **Ship Selection**: Choose which ship to pilot from your fleet

### Star Systems
- **Diverse Types**: Core Worlds, Frontier, Industrial, Military, Research, Trading Hubs, Mining, Agricultural
- **System Properties**: Population, threat levels, resource availability, stations
- **Exploration**: Discover and visit systems to unlock trading and refueling opportunities

### Navigation Options
- **Local Map**: View nearby systems within jump range
- **System Jump**: Travel directly to discovered star systems
- **Coordinate Jump**: Manual navigation to specific X,Y,Z coordinates  
- **Refueling**: Replenish fuel at star systems (10 credits per fuel unit)
- **Galaxy Overview**: Track exploration progress and system discoveries

## Economic System

Experience a realistic supply and demand economy:

### Market Mechanics
- **Dynamic Pricing**: Prices fluctuate based on supply and demand ratios
- **System Specialization**: Different system types produce and consume different goods
  - Industrial systems produce metals and machinery
  - Agricultural worlds grow food and bio-materials  
  - Mining systems extract rare ores and crystals
  - Research stations need exotic materials and data
- **Production Cycles**: Systems continuously produce and consume goods
- **Market Updates**: Prices change when you visit systems or trade

### Trading Features
- **Market Analysis**: View detailed production/consumption data for each system
- **Best Deals**: Automated detection of profitable buying and selling opportunities  
- **Trade Routes**: Identify profitable commodity routes between systems
- **Supply Tracking**: Monitor available quantities and market demand
- **Price History**: Track market trends over time

### Economic Events
Random galaxy-wide events affect markets:
- **Mining Booms**: Increase ore supplies and lower prices
- **Crop Failures**: Reduce food availability and raise prices
- **Trade Wars**: Disrupt supply chains and increase costs
- **Technology Breakthroughs**: Improve production efficiency
- **Pirate Raids**: Reduce luxury good availability

### Strategic Gameplay
- **Arbitrage Opportunities**: Buy low at one system, sell high at another
- **Market Timing**: Wait for favorable events or price fluctuations
- **Cargo Management**: Balance cargo space with profit margins
- **Risk/Reward**: Higher profits often require longer, more dangerous routes

## Galactic Event System

Experience a dynamic galaxy where random events shape the political and economic landscape:

### Event Types
- **Economic Events**: Mining booms, agricultural crises, trade wars, technology breakthroughs, pirate raids, market crashes
- **Political Events**: Diplomatic summits, government overthrows, trade agreements, embargo declarations
- **Scientific Events**: Ancient technology discoveries, quantum anomalies, medical breakthroughs
- **Military Events**: Border skirmishes, fleet mobilizations, peace treaties
- **Natural Events**: Solar flares, asteroid impacts, nebula formations
- **Social Events**: Cultural festivals, labor strikes, celebrity scandals
- **Travel Events**: Pirate activity, navigation beacon failures, wormhole discoveries, space storms
- **Political Scandals**: Humorous PG-13 to R-rated scandals affecting faction relations

### Event Effects
- **Market Impact**: Events alter supply, demand, and prices of commodities across affected systems
- **Travel Hazards**: Dangerous regions increase fuel costs and create navigation warnings
- **Faction Relations**: Political events and scandals affect diplomatic standing with multiple factions
- **System Instability**: Events can increase threat levels and affect system security
- **Duration**: Events last from hours to weeks, with some having permanent effects

### Event Generation
- **Automatic Updates**: Events generate automatically every 5 seconds in the background
- **Probability System**: Different event types have varying chances of occurring
- **Severity Levels**: Events range from 1-10 severity, with higher levels creating breaking news
- **System Targeting**: Events can affect specific star systems or have galaxy-wide impact

## News System

Stay informed about galactic happenings through a comprehensive news network:

### News Categories
- **Breaking News**: High-severity events (6+ severity) requiring immediate attention
- **Economic Reports**: Market trends, trade developments, and financial news
- **Political Updates**: Diplomatic developments, government changes, and policy shifts
- **Scientific Discoveries**: Research breakthroughs, technological advances, and discoveries
- **Military Intelligence**: Conflict reports, fleet movements, and security updates
- **Travel Advisories**: Dangerous regions, navigation hazards, and travel warnings
- **Entertainment & Culture**: Celebrity news, cultural events, and social happenings
- **Political Scandals**: Humorous political scandals and diplomatic embarrassments

### News Features
- **Real-time Updates**: News automatically updates as events occur
- **Categorized Browsing**: Filter news by category for focused reading
- **Travel Advisories**: Get warnings about dangerous regions before traveling
- **Market Analysis**: View economic trends and their causes
- **News Statistics**: Track total news items, breaking news count, and recent activity
- **Multiple Sources**: News comes from various galactic news networks for authenticity

### News Access
- **Simple Text Interface**: Access news through the main menu (option 17)
- **Category Browsing**: View specific types of news (economic, political, etc.)
- **Breaking News Alerts**: High-severity events automatically become breaking news
- **News Summary**: Get formatted overviews of current galactic happenings
- **Force Updates**: Manually trigger new events for testing and exploration

### How to Access News & Events
1. **Modern Interface**: Run `./run_ui.sh` or `python textual_interface.py` for the full graphical experience
2. **Terminal Interface**: Run `python game.py` and select "Galactic News & Events" from main menu
3. **News Categories**: Browse by economic, political, scientific, military, travel, entertainment, or scandal news
4. **Breaking News**: High-severity events automatically appear as breaking news
5. **Travel Advisories**: Check for dangerous regions before navigating
6. **Market Analysis**: View economic trends caused by current events

## Political Scandal System

Experience hilarious political scandals that add humor and affect faction relations:

### Scandal Types
- **Diplomatic Hologram Leak**: Embarrassing private messages and practice sessions
- **Senator's Secret Hobby**: Illegal alien petting zoos and smuggled creatures
- **Ambassador's Dating App Debacle**: Photoshopped dating profiles and awkward bios
- **Space Station Karaoke Scandal**: Naked karaoke sessions and off-key performances
- **Trade Minister's Crypto Scheme**: Quantum coin pyramid schemes and financial scams
- **Fleet Admiral's Collectible Obsession**: Using military resources for trading cards
- **Diplomat's Food Delivery Addiction**: Spending entire budgets on alien pizza
- **Senator's Secret Fan Fiction**: Steamy romance stories about political rivals
- **Ambassador's Gaming Addiction**: Playing games during peace negotiations
- **Council Member's Social Media Meltdown**: Ranting about neighbor's space-lawn decorations

### Scandal Effects
- **Faction Relations**: Scandals damage relations with 1-3 random factions (-5 to -20 points)
- **Severity Levels**: Scandals range from 2-8 severity, often becoming breaking news
- **Duration**: Scandals last 2-14 days, longer than most other events
- **News Coverage**: Each scandal generates multiple catchy headlines and media coverage
- **Diplomatic Impact**: Affects your standing with multiple factions simultaneously

### Scandal Features
- **Humorous Content**: PG-13 to R-rated political humor and absurd situations
- **Real Consequences**: Scandals have genuine gameplay effects on faction relations
- **Variety**: 15+ unique scandal scenarios with different themes and effects
- **News Integration**: Scandals appear in entertainment news with sensational headlines
- **Automatic Generation**: Scandals occur naturally as part of the event system

## Ship Upgrades

Enhance your ships with advanced technology at specialized stations:

### Upgrade Categories
- **Engine Upgrades**: Ion Drive Mk2, Fusion Engine Mk2, Quantum Booster
  - Improve speed, fuel efficiency, and jump range
- **Fuel Systems**: Extended Fuel Tanks, Fuel Recycler, Emergency Reserves  
  - Increase capacity and efficiency for longer journeys
- **Cargo Systems**: Cargo Bay Expansion, Smart Storage, Modular Containers
  - Boost carrying capacity and loading speed
- **Navigation Systems**: Advanced Scanner, Jump Computer, Stellar Cartographer
  - Enhanced sensors, accuracy, and exploration capabilities
- **Defensive Systems**: Reinforced Hull, Shield Booster, Point Defense
  - Better protection and survivability
- **Life Support**: Extended Life Support, Medical Bay, Luxury Quarters
  - Improved crew capacity and comfort

### Upgrade Mechanics
- **Station Requirement**: Upgrades only available at Research Labs, Military Bases, and Shipyards
- **Cost Scaling**: More advanced upgrades cost significantly more
- **Stacking Effects**: Multiple upgrades combine for greater benefits
- **Ship Specialization**: Customize ships for specific roles (trader, explorer, combat)

## Space Station System

Purchase and manage orbital facilities throughout the galaxy:

### Station Types
- **Trading Post** (500k): Market expansion, refueling, repairs
- **Mining Station** (750k): Ore processing, mining equipment  
- **Research Lab** (1M): Technology research, ship upgrades, data analysis
- **Military Base** (1.2M): Weapons, defense systems, ship upgrades
- **Shipyard** (2M): Ship construction, major repairs, full upgrades
- **Luxury Resort** (800k): Entertainment, luxury goods, passenger transport

### Station Features
- **Fixed Locations**: 15-20 stations randomly distributed across star systems
- **Purchase System**: Buy available stations, cannot build new ones
- **Income Generation**: Stations provide passive income based on type and upgrade level
- **Upgrade System**: Improve stations to level 5 for increased income (20% per level)
- **Service Access**: Owned stations provide services like upgrades and specialized trading

### Economic Benefits  
- **Passive Income**: 5k-25k credits per cycle depending on station type
- **Strategic Value**: Control key locations for services and upgrades
- **Empire Building**: Establish presence across multiple systems
- **Investment Growth**: Station upgrades increase long-term profitability

## AI Bot System

Interact with 5 autonomous AI bots that live and act in your galaxy:

### Bot Types
- **Captain Vex** (Trader): Focuses on commerce and trade routes
- **Dr. Cosmos** (Researcher): Seeks research stations and data collection  
- **Explorer Zara** (Explorer): Discovers new systems and surveys space
- **Industrialist Kane** (Industrialist): Builds infrastructure and collects resources
- **Ambassador Nova** (Diplomat): Establishes relations and visits core worlds

### Bot Features
- **Autonomous Behavior**: Bots move independently through the galaxy pursuing their goals
- **Dynamic Personalities**: Each bot has unique traits affecting risk tolerance, trading, and exploration
- **Economic Participation**: Bots buy and sell goods, purchase stations, and compete for resources
- **Player Interaction**: Meet bots at star systems for dialogue, trading, and reputation building
- **Real-time Activity**: Bots operate continuously in background while you play
- **Peaceful NPCs**: No hostile actions - focused on cooperation and trade

### Interaction System
- **Location-based Encounters**: Meet bots when visiting the same star systems
- **Dialogue Options**: Greetings, trade discussions, system information exchange
- **Reputation System**: Build relationships through positive interactions
- **Trading Opportunities**: View bot inventories and trading patterns
- **Status Monitoring**: Track all bot locations, goals, and activities

### Bot Behaviors
- **Goal-driven AI**: Bots pursue specific objectives based on their type
- **Resource Management**: Autonomous fuel, credit, and inventory management
- **Market Participation**: Active buying/selling in the economic system
- **Exploration**: Bots discover and visit new star systems
- **Station Competition**: Bots can purchase available space stations

## Faction System

Engage with 30 unique galactic factions, each with distinct philosophies and goals:

### Major Faction Categories
- **Technology Focused**: The Technotheos, Quantum Artificers Guild, Icaron Collective
- **Research Oriented**: Veritas Covenant, Scholara Nexus, Chemists' Concord
- **Trade & Commerce**: Stellar Nexus Guild, Collective of Commonality, Galactic Salvage Guild
- **Mystical Orders**: Harmonic Resonance Collective, Voidbound Monks, Triune Daughters
- **Cultural Groups**: Galactic Circus, Provocateurs' Guild, Harmonic Synaxis
- **Industrial Powers**: Gearwrights Guild, Ironclad Collective
- **Exploration Guilds**: Stellar Cartographers Alliance, Map Makers, Navigators

### Faction Features
- **Territorial Control**: Factions control 1-3 star systems each across the galaxy
- **Reputation System**: Build relationships from Enemy (-100) to Allied (+100)
- **Dynamic Activities**: Each faction pursues goals based on their philosophy and focus
- **Reputation Benefits**: Unlock faction-specific services, technologies, and bonuses
- **Trade Preferences**: Each faction favors specific commodities and resources
- **Political Complexity**: Factions have relationships with each other affecting diplomacy

### Faction Interactions
- **Territory Indicators**: Systems controlled by factions marked with ⚑ in navigation
- **Reputation Display**: View your standing with all 30 factions
- **Faction Details**: Comprehensive information about each faction's goals and culture
- **Trade Benefits**: Gain reputation through commerce in faction territories
- **Activity Monitoring**: Track what each faction is currently doing
- **Diplomatic Consequences**: Actions affect your reputation with controlling factions

### Sample Factions
- **The Veritas Covenant**: Truth-seeking researchers pursuing universal knowledge
- **Celestial Marauders**: Space pirates roaming the galaxy for treasure and freedom
- **The Gaian Enclave**: Nature guardians balancing technology with ecological harmony
- **Keepers of the Spire**: Ancient guardians protecting mysterious alien artifacts
- **The Brewmasters' Guild**: Master fermenters creating exotic beverages across space

## Profession System

Choose from 30+ unique sci-fi professions that shape your character's abilities and opportunities:

### Profession Categories
- **Scientific**: Astrobiologist, Dimensional Physicist, Quantum Computer Scientist, Galactic Historian
- **Engineering**: Quantum Network Engineer, Terraforming Engineer, Gravity Technician, Energy Harvesting Technician
- **Medical**: Nanomedic, Cybernetic Enhancement Specialist, Regenerative Medicine Specialist, Xeno-neurologist
- **Military**: Temporal Investigator, Chrono-Marine, Dimensional Rift Stabilizer
- **Artistic**: Virtual Reality Architect, Holographic Entertainment Designer, Interstellar Diplomat
- **Mystical**: Soul Architect, Reality Weaver, Void Architect, Etheric Communicator

### Profession Features
- **Character Specialization**: Each profession offers unique abilities and perspectives
- **Experience System**: Gain XP through related activities to level up (1-10 levels)
- **Progressive Benefits**: Unlock new abilities and bonuses as you advance in your profession
- **Job Opportunities**: Find profession-specific work in different star systems
- **Activity Bonuses**: Get enhanced rewards when performing activities related to your expertise
- **Career Development**: Track experience across multiple professions

### Level Progression
- **Level 1-2**: Base benefits and professional recognition
- **Level 3-5**: Intermediate abilities and enhanced effectiveness
- **Level 6-8**: Advanced capabilities and mastery of your field  
- **Level 9-10**: Master-level abilities and transcendent skills

### Sample Professions
- **Astrobiologist**: Study alien life forms and ecosystems across the galaxy
- **Quantum Navigator**: Master quantum propulsion systems for impossible journeys
- **Time Travel Coordinator**: Regulate temporal activities and maintain timeline integrity
- **Reality Weaver**: Manipulate the fabric of local reality using advanced energy fields
- **Interstellar Trade Broker**: Facilitate complex trade agreements between star systems

## File Structure

### Core Game Files
- `game.py` - Main game logic with terminal-based interface
- `textual_interface.py` - Modern ASCII interface using Textual framework
- `events.py` - Dynamic galactic event system with 8 event types
- `news_system.py` - Comprehensive news feed and reporting system
- `professions.py` - 30+ sci-fi professions with experience and career progression
- `factions.py` - 30 galactic factions with diplomacy and territory systems
- `ai_bots.py` - AI bot system with autonomous NPCs
- `economy.py` - Dynamic supply/demand economic system with market simulation
- `station_manager.py` - Ship upgrade system and space station management
- `navigation.py` - 3D space navigation and galaxy generation system
- `characters.py` - Character classes, backgrounds, and stats system
- `ship_builder.py` - Ship construction system with components and templates
- `manufacturing.py` - Industrial platform definitions
- `goods.py` - Commodity and resource catalog
- `ship_classes.py` - Starship class definitions
- `space_stations.py` - Space station types
- `galactic_history.py` - Archaeological sites and ancient civilizations

### Launcher Scripts
- `run_ui.sh` - Modern interface launcher with mouse support
- `requirements_ui.txt` - Dependencies for the modern interface

## Game World

Set in the far future where humanity has spread across the galaxy using advanced technologies:

- **Ether Magic**: Mystical energy that powers advanced technologies
- **Exotic Materials**: Rare resources like Gravossils, Aetheron Vapors, and Quantum Sand
- **Advanced Manufacturing**: From BioWeave Looms to Singularity Reactors
- **Interstellar Commerce**: Trade routes spanning multiple star systems
- **Diverse Civilizations**: Various alien races and post-human societies

## Current Features

The game now includes:
- ✅ **Random Events and Encounters**: Dynamic event system with 8 event types
- ✅ **Galactic News System**: Comprehensive news feed with breaking news and categories
- ✅ **Political Scandals**: Humorous scandal system affecting faction relations
- ✅ **Diplomatic Relations**: 30 factions with reputation and territory systems
- ✅ **Galaxy Map and Exploration**: 3D navigation with 30-40 star systems
- ✅ **Production Chains**: Manufacturing platforms and economic simulation
- ✅ **AI Bot System**: 5 autonomous NPCs with unique personalities
- ✅ **Archaeological System**: Ancient sites and civilizations to discover
- ✅ **Modern Interface**: Textual-based retro ASCII interface with mouse support

## Future Expansion Ideas

Potential additions for future development:
- Save/load game functionality
- Combat system with ship battles
- Technology research trees
- Multiplayer capabilities
- Expanded event types and scenarios
- More complex diplomatic negotiations
- Player-created content and modding support

## Requirements

- Python 3.x
- Terminal/command line interface
- No additional dependencies required

## License

Open source - feel free to modify and expand upon this game!
