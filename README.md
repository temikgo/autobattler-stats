# Backpack Brawl Statistics Tracker

A Python tool for collecting and analyzing gameplay statistics from Backpack Brawl (autobattler/item management game).

## Features

- Track match history with detailed game data
- Record items used, opponents faced, and match outcomes
- Comprehensive statistics analysis:
  - Win rates (overall, vs specific heroes, with specific items)
  - Item usage frequency
  - Rating progression
  - Trophy performance
- Visual data representation (graphs, charts)

## Installation

1. Ensure you have Python 3.6+ installed
2. Clone this repository or download the source files
3. No additional dependencies required (uses standard Python libraries)

## Usage

### Adding New Game Data

Run the updater to input your match results:
```bash
python3 updater.py
```

Follow the prompts to enter:
1. Your username (creates/updates your personal stats file)
2. Match details (start/end rating, hero used)
3. Game data (win/loss, opponent details, items used)

### Viewing Statistics

Run the stats displayer to analyze your performance:
```bash
python3 stats_displayer.py
```

After entering your username, choose from available statistics:

1. Rating Progress - Track your rating changes over time
2. Win Rate vs Heroes - Your performance against different heroes
3. Item Usage - How frequently you use each item
4. Item Binary Usage - Whether you used items (regardless of quantity)
5. Item Win Rate - Win rate when using specific items
6. Item Binary Win Rate - Win rate when using items (regardless of quantity)
7. Game Win Rate - Your overall win rate
8. Trophy Win Rate - Performance with different trophy counts

## Data Structure

All statistics are saved in JSON format in the `data/` directory:
- Each user has their own `[username]_stats.json` file
- Data is organized by matches containing individual games
- Includes all relevant gameplay information for analysis

## Customization

### Adding New Statistics

1. Create a new class in `stats.py` that inherits from `StatisticsFunction`
2. Implement the `display()` method with your analysis logic
3. Add your class to the `available_stats` list in `stats_displayer.py`

### Updating Game Constants

Modify `constants.py` to:
- Add new heroes (update `HEROES` list)
- Add new items (update `ITEMS` list)

## Example Use Case

1. After each gaming session, run `updater.py` to record your matches
2. Periodically run `stats_displayer.py` to:
   - Identify your strongest/weakest heroes
   - Discover most effective item combinations
   - Track rating improvement over time
3. Use insights to refine your gameplay strategy

## Contributing

Contributions are welcome! Please open an issue or pull request for:
- New statistical analyses
- Improved visualization options
- Additional game constants
- Bug fixes
