import random
import json
import discord
from discord.ext import commands
import os
from collections import defaultdict

class Player:
    def __init__(self, name, role=None, hero=None, rank=None, stats=None):
        self.name = name
        self.role = role
        self.hero = hero
        self.rank = rank if rank else 1000
        self.hero_selection_count = {}
        self.hero_ban_count = {}
        self.wins = 0
        self.losses = 0
        self.pb_rank = 1000
        self.stats = {'wins': 0, 'losses': 0, 'pb_wins': 0, 'pb_losses': 0}
        self.hero_selection_count = {}
        self.hero_ban_count = {}
        self.hero_selection_count = defaultdict(int)
        self.hero_ban_count = defaultdict(int)

    def win_rate(self):
        total_wins = self.stats['wins'] + self.stats['pb_wins']
        total_losses = self.stats['losses'] + self.stats['pb_losses']
        if total_wins == 0 and total_losses == 0:
            return 0
        return total_wins / (total_wins + total_losses) * 100

    def increment_hero_ban_count(self, hero):
        if hero not in self.hero_ban_count:
            self.hero_ban_count[hero] = 0
        self.hero_ban_count[hero] += 1

    def increment_hero_selection_count(self, hero):
        if hero not in self.hero_selection_count:
            self.hero_selection_count[hero] = 1
        else:
            self.hero_selection_count[hero] += 1

    def most_selected_hero(self):
        if not self.hero_selection_count:
            return "N/A"
        most_selected_hero = max(self.hero_selection_count, key=self.hero_selection_count.get)
        return most_selected_hero

    def update_pb_rank(self, delta):
        self.pb_rank += delta
        self.pb_rank = max(min(self.pb_rank, 10000), 0)

roles = ["Carry", "Support", "Solo", "Jungle", "Mid"]
heroes = {
    "Twinblast", "Sparrow", "Wraith", "Murdock", "Revenant", "Steel", "Maco", "Muriel", "Dekker", "Narbash", "Serath", "Aurora", "Rampage", "Feng Mao", "Countess", "Shinbi", "Zena", "Grux", "Sevarog", "Khaimera", "Kallari", "Wukong", "Crunch", "Gideon", "The Fey", "Howitzer", "Belica", "Gadget", "Phase"
}
available_heroes = {
    "Twinblast", "Sparrow", "Wraith", "Murdock", "Revenant", "Steel", "Maco", "Muriel", "Dekker", "Narbash", "Serath", "Aurora", "Rampage", "Feng Mao", "Countess", "Shinbi", "Zena", "Grux", "Sevarog", "Khaimera", "Kallari", "Wukong", "Crunch", "Gideon", "The Fey", "Howitzer", "Belica", "Gadget", "Phase"
}
roles_and_heroes = {"Carry": ["Twinblast", "Sparrow", "Wraith", "Murdock", "Revenant"],
    "Support": ["Steel", "Maco", "Muriel", "Dekker", "Narbash"],
    "Solo": ["Serath", "Aurora", "Rampage", "Feng Mao", "Countess", "Shinbi", "Zena"],
    "Jungle": ["Grux", "Sevarog", "Khaimera", "Kallari", "Wukong", "Crunch"],
    "Mid": ["Gideon", "The Fey", "Howitzer", "Belica", "Gadget", "Phase"]
}


def assign_roles_and_heroes(team):
    assigned_roles = random.sample(list(roles_and_heroes.keys()), len(team))
    for i, player in enumerate(team):
        player.role = assigned_roles[i]
        player.hero = random.choice(roles_and_heroes[player.role])

    roles = list(roles_and_heroes.keys())

    while len(roles) < len(team):
        roles.extend(list(roles_and_heroes.keys()))
        
    random.shuffle(roles)

    for i, player in enumerate(team):
        role = roles[i]
        hero = random.choice(roles_and_heroes[role])
        player.role = role
        player.hero = hero
        player.increment_hero_selection_count(hero)

    return team

def update_pb_rank(winning_team, losing_team, k=32):
    for winner in winning_team:
        for loser in losing_team:
            winner_expected = 1 / (1 + 10 ** ((loser.pb_rank - winner.pb_rank) / 400))
            loser_expected = 1 / (1 + 10 ** ((winner.pb_rank - loser.pb_rank) / 400))

            winner.pb_rank += k * (1 - winner_expected)
            loser.pb_rank += k * (0 - loser_expected)

def display_available_heroes(available_heroes):
    print("\nAvailable heroes:")
    for hero in sorted(available_heroes):
        print(hero)

def load_players(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            return [Player(name, rank=p['rank'], stats=p['stats']) for name, p in data.items()]
    return []

def save_players(file_path, players):
    data = {p.name: {'rank': p.rank, 'stats': p.stats} for p in players}
    with open(file_path, 'w') as f:
        json.dump(data, f)

def create_teams(players):
    players = sorted(players, key=lambda x: x.rank, reverse=True)
    team1 = []
    team2 = []

    while players:
        if len(team1) <= len(team2):
            player = random.choice(players)
            team1.append(player)
            players.remove(player)
        else:
            player = random.choice(players)
            team2.append(player)
            players.remove(player)

    team1 = assign_roles_and_heroes(team1)
    team2 = assign_roles_and_heroes(team2)

    return team1, team2

def display_teams(team1, team2, show_heroes_and_roles=True):
    if show_heroes_and_roles:
        print("\n-------------- TEAM 1 -------------:")
        print("{:<15} {:<10} {:<10}".format("Player", "Hero", "Role"))
        print("-" * 35)
    else:
        print("\n-------------- TEAM 1 -------------:")
        print("{:<15}".format("Player"))

    for player in team1:
        hero = player.hero if player.hero is not None else "N/A"
        role = player.role if player.role is not None else "N/A"
        if show_heroes_and_roles:
            print("{:<15} {:<10} {:<10}".format(player.name, hero, role))
        else:
            print("{:<15}".format(player.name))

    if show_heroes_and_roles:
        print("\n=====================================")

    if show_heroes_and_roles:
        print("\n-------------- TEAM 2 -------------:")
        print("{:<15} {:<10} {:<10}".format("Player", "Hero", "Role"))
        print("-" * 35)
    else:
        print("\n-------------- TEAM 2 -------------:")
        print("{:<15}".format("Player"))

    for player in team2:
        hero = player.hero if player.hero is not None else "N/A"
        role = player.role if player.role is not None else "N/A"
        if show_heroes_and_roles:
            print("{:<15} {:<10} {:<10}".format(player.name, hero, role))
        else:
            print("{:<15}".format(player.name))
    
def update_rank(winning_team, losing_team, k=32):
    for winner in winning_team:
        winner.stats['wins'] += 1
        for loser in losing_team:
            rank_diff = loser.rank - winner.rank
            expected_outcome = 1 / (1 + 10 ** (rank_diff / 400))
            winner.rank += k * (1 - expected_outcome)
            loser.rank -= k * (1 - expected_outcome)

    for loser in losing_team:
        loser.stats['losses'] += 1

def get_player_names(num_players):
    player_names = []
    for i in range(num_players):
        name = input(f"Enter the name for player {i + 1}: ")
        player_names.append(name)
    return player_names

def update_stats(player, result, winning_team, losing_team):
    if result == "win":
        player.stats['wins'] += 1
        delta_rank = calculate_rank_change(player.rank, losing_team)
        player.update_rank(delta_rank)
        player.stats['pb_wins'] += 1
        pb_delta_rank = calculate_rank_change(player.pb_rank, losing_team)
        player.update_pb_rank(pb_delta_rank)
    elif result == "loss":
        player.stats['losses'] += 1
        delta_rank = calculate_rank_change(player.rank, winning_team)
        player.update_rank(-delta_rank)
        player.stats['pb_losses'] += 1
        pb_delta_rank = calculate_rank_change(player.pb_rank, winning_team)
        player.update_pb_rank(-pb_delta_rank)

def pick_heroes(team1, team2, available_heroes):
    for i in range(len(team1)):
        for team in [team1, team2]:
            team_num = 1 if team == team1 else 2
            player = team[i]
            print(f"\nTeam {team_num} picks for {player.name}:")
            hero = input("Enter the hero: ")
            while hero not in available_heroes:
                print("Invalid hero name or hero not available. Please enter a valid hero:")
                hero = input("Enter the hero: ")
            available_heroes.remove(hero)

            player.hero = hero
            player.increment_hero_selection_count(hero)

        print("\nTeam 1:")
        print("{:<15} {:<10}".format("Player", "Hero"))
        print("-" * 25)
        for player in team1:
            print("{:<15} {:<10}".format(player.name, player.hero))

        print("\nTeam 2:")
        print("{:<15} {:<10}".format("Player", "Hero"))
        print("-" * 25)
        for player in team2:
            print("{:<15} {:<10}".format(player.name, player.hero))

def pick_and_ban(selected_players, heroes, bans_per_team=1):
    random.shuffle(selected_players)
    team1_players = selected_players[:len(selected_players) // 2]
    team2_players = selected_players[len(selected_players) // 2:]

    available_heroes = set(heroes)

    for i in range(bans_per_team):
        for team, banning_player in [(team1_players, team1_players[-1]), (team2_players, team2_players[-1])]:
            print(f"\nTeam {1 if team == team1_players else 2} bans by {banning_player.name}:")
            hero_to_ban = input("Enter the hero to ban: ").strip()
            banning_player.increment_hero_ban_count(hero_to_ban)

    for i in range(len(selected_players)//2):
        for team, picking_player in [(team1_players, team1_players[i]), (team2_players, team2_players[i])]:
            print(f"\nTeam {1 if team == team1_players else 2} picks:")
            hero_to_pick = input(f"Enter the hero for player {picking_player.name}: ").strip()
            picking_player.hero = hero_to_pick
            picking_player.increment_hero_selection_count(hero_to_pick)

    return team1_players, team2_players


def main():
    file_path = "players.json"
    players = load_players(file_path)
    
    while True:
        print("\n============= MAIN MENU =============")
        print("1. Check Player Stats")
        print("2. Create Players")
        print("3. Start Randomizer")
        print("4. Custom Pick and Ban")
        print("5. Exit")
        choice = input("Enter your choice (1/2/3/4): ")
        print("=====================================")

        if choice == '1':
           if players:
               print("\nPlayer Stats:")
               print("{:<20} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<25} {:<10}".format("Name", "ARAM Rank", "PB Rank", "ARAM W's", "ARAM L's", "PB Wins", "PB Losses", "Most Played Hero", "Overall Win rate"))
               print("-" * 160)
               for player in players:
                   print("{:<20} {:<10.2f} {:<10.2f} {:<10} {:<10} {:<10} {:<10} {:<25} {:<10.2f}%".format(player.name, player.rank, player.pb_rank, player.stats['wins'], player.stats['losses'], player.stats['pb_wins'], player.stats['pb_losses'], player.most_selected_hero(), player.win_rate()))
               print("-" * 160)
           else:
               print("No players found. Add players by choosing 'Create players' from the menu.")
            
        elif choice == '2':
            player_names = input("Enter player names separated by comma: ").split(',')
            new_players = [Player(name.strip()) for name in player_names]
            players.extend(new_players)
            print("Players added successfully.")
        elif choice == '3':
            if not players:
                print("No players found. Add players by choosing 'Create players' from the menu.")
                continue

            selected_players = []
            print("\nSelect players for the match:")
            for i, player in enumerate(players):
                print(f"{i + 1}. {player.name}")

            selected_indices = input("Enter player numbers separated by commas (e.g., 1,2,3): ").split(',')
            for index in selected_indices:
                selected_players.append(players[int(index) - 1])

            while True:
                team1, team2 = create_teams(selected_players)
                display_teams(team1, team2)

                print()  # Add an extra newline for better readability
                print("Options:")
                print("  1. Team 1 wins")
                print("  2. Team 2 wins")
                print("  r. Reshuffle Teams")
                print("  q. Quit to Menu")
                winner = input("Choose an option: ")

                if winner == '1':
                    update_rank(team1, team2)
                elif winner == '2':
                    update_rank(team2, team1)
                elif winner.lower() == 'r':
                    pass  # Simply reshuffle without updating ranks
                elif winner.lower() == 'q':
                    break

                reshuffle = input("Reshuffle teams? (Y/N): ")
                if reshuffle.lower() != 'y':
                    break

                print("=====================================")  # Add an extra newline for better readability
        elif choice == '4':
            if len(players) < 4:
                print("Not enough players. Please create at least 4 players to proceed.")
                continue
            selected_players = []
            print("\nSelect players for the custom pick and ban game:")
            for i, player in enumerate(players):
                print(f"{i + 1}. {player.name}")

            selected_indices = input("Enter player numbers separated by commas (e.g., 1,2,3): ").split(',')
            for index in selected_indices:
                selected_players.append(players[int(index) - 1])

            team1, team2 = pick_and_ban(selected_players, heroes, bans_per_team=1)

            display_teams(team1, team2)

            result = int(input("\nMatch result:\n  1. Team 1 wins\n  2. Team 2 wins\nChoose an option: "))

            if result == 1:
                update_pb_rank(team1, team2)
                for player in team1:
                    player.wins += 1
                    player.stats['pb_wins'] += 1
                for player in team2:
                    player.losses += 1
                    player.stats['pb_losses'] += 1
            elif result == 2:
                update_pb_rank(team2, team1)
                for player in team1:
                    player.losses += 1
                    player.stats['pb_losses'] += 1
                for player in team2:
                    player.wins += 1
                    player.stats['pb_wins'] += 1              


        elif choice == '5':
              break

        else:
              print("Invalid input. Please enter a valid option.")

    save_players(file_path, players)
    data = {p.name: {'rank': p.rank, 'stats': p.stats, 'hero_selection_count': p.hero_selection_count} for p in players}
    with open(file_path, 'w') as f:
        json.dump(data, f)


if __name__ == "__main__":
    main()

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command()
async def aram(ctx, *args):
    input_data = list(args)
    result = main(input_data)
    await ctx.send(result)

bot_token = "MTA5OTUwNjkwNTA0ODY4MjUwNg.GENgbX.ZrmGVA-19168iP2OR0JgPzTm0KSZ0USA2K5eDc"
client.run(bot_token)
