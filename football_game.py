import random
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class TeamSide(Enum):
    HOME = "Home"
    AWAY = "Away"

class PlayType(Enum):
    PASS = "Pass"
    RUN = "Run"
    PUNT = "Punt"
    FIELD_GOAL = "Field Goal"

@dataclass
class Player:
    name: str
    number: int
    position: str
    speed: int  # 1-100
    strength: int  # 1-100
    accuracy: int  # 1-100 (for QBs)

@dataclass
class Team:
    name: str
    side: TeamSide
    players: list
    score: int = 0
    possession: bool = False
    
    def add_player(self, player: Player):
        self.players.append(player)
    
    def get_player_by_position(self, position: str) -> Optional[Player]:
        for player in self.players:
            if player.position == position:
                return player
        return None

class Field:
    """Represents the football field"""
    FIELD_LENGTH = 100  # yards
    ENDZONE_LENGTH = 10  # yards
    
    def __init__(self):
        self.ball_position = 20  # Starting position for kickoff
        self.down = 1
        self.yards_to_go = 10
    
    def reset_downs(self):
        self.down = 1
        self.yards_to_go = 10
    
    def advance_ball(self, yards: int):
        self.ball_position += yards
        self.down += 1
    
    def is_touchdown(self) -> bool:
        return self.ball_position >= Field.FIELD_LENGTH
    
    def is_out_of_bounds(self) -> bool:
        return self.ball_position < 0 or self.ball_position > (Field.FIELD_LENGTH + Field.ENDZONE_LENGTH)

class Game:
    def __init__(self, home_team: Team, away_team: Team):
        self.home_team = home_team
        self.away_team = away_team
        self.field = Field()
        self.current_possession = home_team
        self.quarter = 1
        self.time_remaining = 900  # 15 minutes per quarter in seconds
        self.game_over = False
    
    def display_scoreboard(self):
        """Display current game status"""
        print("\n" + "="*50)
        print(f"QUARTER: {self.quarter} | TIME: {self.time_remaining // 60}:{self.time_remaining % 60:02d}")
        print("="*50)
        print(f"{self.home_team.name:20} {self.home_team.score:3}")
        print(f"{self.away_team.name:20} {self.away_team.score:3}")
        print("="*50)
        print(f"Ball Position: {self.field.ball_position} yards")
        print(f"Down: {self.field.down} | Yards to Go: {self.field.yards_to_go}")
        print(f"Possession: {self.current_possession.name}")
        print("="*50)
    
    def execute_play(self, play_type: PlayType) -> int:
        """Execute a play and return yards gained"""
        qb = self.current_possession.get_player_by_position("QB")
        
        if play_type == PlayType.PASS and qb:
            # Pass play
            accuracy_factor = qb.accuracy / 100
            base_yards = random.randint(5, 20)
            completion_chance = accuracy_factor * 0.8  # 80% max completion
            
            if random.random() < completion_chance:
                yards_gained = base_yards + random.randint(-2, 5)
                print(f"✓ Complete! {yards_gained} yards gained!")
                return yards_gained
            else:
                print("✗ Incomplete pass!")
                return 0
        
        elif play_type == PlayType.RUN:
            # Run play
            rb = self.current_possession.get_player_by_position("RB")
            if rb:
                speed_factor = rb.speed / 100
                strength_factor = rb.strength / 100
                base_yards = random.randint(3, 12)
                yards_gained = int(base_yards * (speed_factor + strength_factor) / 2)
                print(f"Run play! {yards_gained} yards gained!")
                return yards_gained
            return 0
        
        elif play_type == PlayType.FIELD_GOAL:
            # Field goal attempt
            kicker = self.current_possession.get_player_by_position("K")
            if kicker and self.field.ball_position >= 35:  # Inside opponent's 45-yard line
                success_chance = 0.7 if self.field.ball_position >= 50 else 0.8
                if random.random() < success_chance:
                    print("✓ Field Goal Good! 3 points!")
                    return 3
                else:
                    print("✗ Field Goal Missed!")
                    return 0
            return 0
        
        return 0
    
    def process_drive(self):
        """Process one offensive drive"""
        print(f"\n{self.current_possession.name} on offense!")
        self.field.reset_downs()
        
        while self.field.down <= 4:
            self.display_scoreboard()
            
            # Choose play
            play_choice = random.choice([PlayType.PASS, PlayType.RUN])
            
            print(f"\n>>> {self.current_possession.name} calls {play_choice.value}!")
            yards_gained = self.execute_play(play_choice)
            
            # Update field position
            self.field.advance_ball(yards_gained)
            self.field.yards_to_go -= yards_gained
            
            # Check for touchdown
            if self.field.is_touchdown():
                self.current_possession.score += 6
                print(f"\n🏈 TOUCHDOWN {self.current_possession.name}! 6 points!")
                # Extra point attempt
                self.attempt_extra_point()
                self.change_possession()
                return
            
            # Check for first down
            if self.field.yards_to_go <= 0:
                print(f"\n✓ FIRST DOWN {self.current_possession.name}!")
                self.field.yards_to_go = 10
                self.field.down = 1
            
            # Check for turnover on downs
            if self.field.down > 4:
                print(f"\n✗ TURNOVER ON DOWNS!")
                self.change_possession()
                return
        
        self.change_possession()
    
    def attempt_extra_point(self):
        """Attempt extra point after touchdown"""
        print("\nExtra point attempt: 1 for field goal, 2 for conversion")
        choice = random.choice([1, 2])
        
        if choice == 1:
            if random.random() < 0.95:  # High success rate for 1-point
                self.current_possession.score += 1
                print("✓ Extra point good!")
            else:
                print("✗ Extra point missed!")
        else:
            if random.random() < 0.5:  # 50% success for 2-point conversion
                self.current_possession.score += 2
                print("✓ 2-point conversion successful!")
            else:
                print("✗ 2-point conversion failed!")
    
    def change_possession(self):
        """Change possession to the other team"""
        self.current_possession = self.away_team if self.current_possession == self.home_team else self.home_team
        self.field.ball_position = 20  # Reset to 20-yard line for new possession
        self.field.reset_downs()
    
    def advance_quarter(self):
        """Advance to next quarter"""
        self.quarter += 1
        self.time_remaining = 900 if self.quarter <= 4 else 0
        if self.quarter > 4:
            self.game_over = True
    
    def play_game(self, drives_per_quarter: int = 2):
        """Play the entire game"""
        print(f"\n🏈 {self.home_team.name} vs {self.away_team.name} 🏈")
        print("="*50)
        
        for quarter in range(1, 5):
            print(f"\n--- QUARTER {quarter} START ---")
            for drive in range(drives_per_quarter):
                self.process_drive()
                input("\nPress Enter for next drive...")
            self.advance_quarter()
        
        self.display_final_score()
    
    def display_final_score(self):
        """Display final game score"""
        print("\n" + "="*50)
        print("FINAL SCORE")
        print("="*50)
        print(f"{self.home_team.name:20} {self.home_team.score}")
        print(f"{self.away_team.name:20} {self.away_team.score}")
        print("="*50)
        
        if self.home_team.score > self.away_team.score:
            print(f"🏆 {self.home_team.name} WINS! 🏆")
        elif self.away_team.score > self.home_team.score:
            print(f"🏆 {self.away_team.name} WINS! 🏆")
        else:
            print("🤝 It's a TIE! 🤝")

def create_sample_teams():
    """Create sample teams with players"""
    home_team = Team("Home Hawks", TeamSide.HOME, [])
    away_team = Team("Away Falcons", TeamSide.AWAY, [])
    
    # Add players to home team
    home_team.add_player(Player("Patrick Mahomes", 15, "QB", 85, 90, 95))
    home_team.add_player(Player("Isiah Pacheco", 10, "RB", 92, 88, 0))
    home_team.add_player(Player("Mecole Hardman", 12, "WR", 95, 80, 0))
    home_team.add_player(Player("Harrison Butker", 5, "K", 70, 75, 98))
    
    # Add players to away team
    away_team.add_player(Player("Josh Allen", 17, "QB", 88, 92, 90))
    away_team.add_player(Player("James Cook", 28, "RB", 90, 85, 0))
    away_team.add_player(Player("Stefon Diggs", 14, "WR", 93, 82, 0))
    away_team.add_player(Player("Tyler Bass", 2, "K", 72, 76, 96))
    
    return home_team, away_team

def main():
    """Main game function"""
    print("\n🏈 AMERICAN FOOTBALL GAME 🏈\n")
    
    home_team, away_team = create_sample_teams()
    game = Game(home_team, away_team)
    
    game.play_game(drives_per_quarter=1)

if __name__ == "__main__":
    main()
