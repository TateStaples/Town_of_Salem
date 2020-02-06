# all of november and december 2019

import socket
import select
import time
import threading
import Players
from random import choice

class Game:
    # defines variables
    def __init__(self):
        # give object
        Players.main = self

        # day that we are on
        self.day_at = 0

        # name, socket dictionary
        self.players = {}

        # name, role dictionary
        self.roles = {}

        # list of mafia names for night chat and see team
        self.mafia_members = []

        # list of coven members for night chat and stuff
        self.coven_members = []

        # list of vampires
        self.vampires = []

        # list of live player sockets
        self.alive_players = []

        # list of dead player sockets
        self.dead_players = []

        # list of all sockets
        self.socket_list = []

        # if in the voting period
        self.voting = False

        # if nomination period
        self.nominating = False

        # dictionary of living players and their nomination counts
        self.nomination_counts = {}

        # will store name of the accused to prevent their voting in own lynching
        self.accused = ""

        # dicitonary of each person and their votes
        self.votes = {}

        # True if day, False if night... used for chat spread
        self.is_day = True

        # what stage of night at
        self.night_stage = 0

    # accepts the players as they join
    def login(self):
        player_count = int(input("How many players are you accepting?   "))
        amount_of_players = 0

        # accept players
        while amount_of_players < player_count:
            connecting_socket, address = s.accept()
            #print(connecting_socket)
            print(f"Connected to {address}")
            amount_of_players += 1
            connecting_socket.send(bytes("Welcome to the server\n", byte_type))  # the utf-8 is the type of bytes
            time.sleep(.01)
            connecting_socket.send(bytes(f"There are currently {amount_of_players} people on the server\n", byte_type))
            # this is the username
            received_name = connecting_socket.recv(10).decode(byte_type)
            msg = ""
            for char in received_name:
                if char in valid_chars:
                    msg += char
            msg = msg.replace(" ", "_")

            print(f"Their username is {msg}.")
            self.players[msg] = connecting_socket
            self.alive_players.append(msg)
            self.socket_list.append(connecting_socket)
        print("login over...")

    # gives each player their role - maybe do wholisticly
    def assign_roles(self):
        print("assigning roles...")
        exe = []
        for person in self.players:
            role = Players.assign_role(person)
            self.send(person, f"You are a {role.name}")
            self.roles[person] = role
            if role.name == "Executioner":
                exe.append(role)
        # give executioners their targets
        for e in exe:
            e.assign_target()

    # checks to see if the game is over
    def game_over(self):
        # check for draws - no kills 2 days in a row (after day 7)
        if len(self.alive_players) <= 1:
            return True

        # mutually exclusive factions
        all_factions = [
            "Town", "Mafia", "Coven", # normal groups
            "Vampire", "Plague Bearer", "Arsonist",
            "Werewolf", "Serial Killer", "Juggernaut"  # neutral types
        ]

        # factions with living members
        remaining_factions = []

        # if there is witch, Town not win
        is_witch = False

        for player in self.alive_players:
            role = self.roles[player]

            # check if player is witch
            if role.name == "Witch":
                is_witch = True

            # check for neutral types
            elif role.name in all_factions and role.name not in remaining_factions:
                remaining_factions.append(role.name)

            # check major groups
            elif role.type in all_factions and role.type not in remaining_factions:
                remaining_factions.append(role.type)

        # check for competing factions
        if len(remaining_factions) > 1:
            return False

        # returns False if witch and town
        if "Town" in remaining_factions and is_witch:
            return False

        return True

    # is the main method... runs the game on permanent loop until game_over
    def play_game(self):

        # get players to join
        self.login()

        # give each player a role from Players
        self.assign_roles()

        t1 = threading.Thread(target=self.read_messages)
        t1.start()

        while not self.game_over():
            self.run_day()
            self.day_at += 1
            self.run_night()
        Players.main = self
        winners = []
        for player in self.roles:
            if self.roles[player].winner():
                winners.append(player)

        self.broadcast(f"The winners are: {winners}")
        self.broadcast("game over!")
        t1.join()

    # runs the different sessions of the day
    def run_day(self):
        self.broadcast(f"The dawn of a new day has arrived. Day {self.day_at} has begun!")
        print("a new day...")
        self.nominating = False
        self.is_day = True
        day_length = 30
        start_time = time.process_time()//1
        previous_time = start_time
        while self.is_day:
            current_time = time.process_time() // 1
            remaining = int(day_length - (current_time - start_time))
            if current_time != previous_time and remaining in countdown:
                self.broadcast(countdown[remaining])
            previous_time = current_time
            if current_time - start_time >= day_length and not self.nominating:
                self.enter_nominating()
                break

    # runs the night time events
    def run_night(self):
        print("another spooky night")
        self.broadcast("a new night has begun")
        if self.day_at % 2 == 0:
            self.broadcast("Tonight is a full moon")
        self.is_day = False
        night_length = 45
        for player in self.alive_players:
            self.roles[player].reset()
        start_time = time.process_time()
        previous_time = start_time
        self.night_stage = 0
        # give necronomicon if no one has it
        if self.day_at >= 3: self.give_necronomicon()
        while not self.is_day:
            current_time = time.process_time() // 1
            remaining = int(night_length - (current_time - start_time))
            if current_time != previous_time and remaining in countdown:
                self.broadcast(countdown[remaining])
            previous_time = current_time
            if current_time-start_time >= night_length:  # if the night has ended
                self.night_stage = 1
                for player in self.players:
                    role = self.roles[player]
                    if role.can_target():
                        self.roles[player].activate_target_1()
                self.night_stage = 2
                for player in self.players:
                    role = self.roles[player]
                    if role.can_target():
                        self.roles[player].activate_target_2()
                self.night_stage = 3
                for player in self.players:
                    role = self.roles[player]
                    if role.can_target():
                        self.roles[player].activate_target_3()
                self.night_stage = 4
                for player in self.players:
                    role = self.roles[player]
                    if role.can_target():
                        self.roles[player].activate_target_4()
                self.night_stage = 5
                for player in self.players:
                    role = self.roles[player]
                    if role.can_target():
                        self.roles[player].activate_target_5()
                self.night_stage = 6
                for player in self.players:
                    role = self.roles[player]
                    if role.can_target():
                        self.roles[player].activate_target_6()

                # carry out all the deaths - death is a dictionary of person and means
                for victim in Players.Player.deaths:
                    self.send(victim, "You have died!")
                    self.kill(victim, Players.Player.deaths[victim])
                Players.Player.deaths = {}
                self.is_day = True
        self.night_stage = 0

    # starts the nomination session
    def enter_nominating(self):
        print("nominations...")
        self.nominating = True
        nominating_length = 30
        self.nomination_counts = {}
        self.votes = {}
        self.broadcast("*** Nominations have begun ***")
        start_time = time.process_time()//1
        previous_time = start_time
        while self.nominating:
            for nomination in self.nomination_counts:  # can get error if someone nominates while this is running
                if self.nomination_counts[nomination] > len(self.alive_players) / 2:
                    self.accused = nomination
                    self.enter_voting()
                    break
            current_time = time.process_time() // 1
            remaining = int(nominating_length - (current_time - start_time))
            if current_time != previous_time and remaining in countdown:
                self.broadcast(countdown[remaining])
            previous_time = current_time
            if current_time-start_time >= nominating_length:
                break

    # starts a voting period
    def enter_voting(self):
        print("voting...")
        self.broadcast("*** voting has begun ***")
        self.nominating = False
        self.voting = True
        voting_length = 20
        self.votes = {}
        self.broadcast(f"{self.accused} has been voted up! vote now")
        start_time = time.process_time() // 1
        previous_time = start_time
        while self.voting:
            current_time = time.process_time() // 1
            remaining = int(voting_length - (current_time - start_time))
            if current_time != previous_time and remaining in countdown:
                self.broadcast(countdown[remaining])
            previous_time = current_time
            if current_time-start_time >= voting_length:
                guilty_counter = 0
                for vote in self.votes:
                    guilty_counter += self.votes[vote]
                if guilty_counter > 0:
                    self.lynch(self.accused)
                for player in self.players:
                    if player not in self.votes:
                        self.broadcast(player + " abstained")
                    elif self.votes[player] == 0:
                        self.broadcast(player + " abstained")
                    elif self.votes[player] > 0:
                        self.broadcast(player + " voted guilty")
                    elif self.votes[player] < 0:
                        self.broadcast(player + " voted innocent")

                self.voting = False
                self.accused = ""

    # lynches the accused (essentially kill but checks for Jest and Exe first)
    def lynch(self, target):
        # check if accused is Jest to activate wins
        if self.roles[target].name == "Jester":
            self.roles[target].has_won = True
            self.roles[target].day_i_died = self.day_at
            self.send(target, "You won! Sneaky jest")
        # check if target was an Exe target
        for player in self.alive_players:
            if self.roles[player].name == "Executioner" and self.roles[player].my_target == target:
                self.roles[player].has_won = True
                self.send(target, "You won!")
        self.kill(target, "lynched")

    # removes a player if they disconnect
    def disconnect(self, socket):
        for player in self.players:
            if self.players[player] == socket:
                self.players.pop(player)
                self.socket_list.remove(socket)
                self.kill(player, "smited for quitting mid-game")
                break
        else:
            print("could disconnect that player")

    # changes target from alive to dead and broadcasts role and kill method
    def kill(self, target, means):
        self.broadcast(f"{target} has been {means}")
        self.broadcast(f"{target} was a {self.roles[target].death_name}")
        self.alive_players.remove(target)
        self.dead_players.append(target)
        print(self.dead_players)

    # takes each received message, decodes it, and sends it to processing
    def read_messages(self):
        while True:  # this ends in the play_game function
            read_sockets, write_socket, error_socket = select.select(self.socket_list, [], [])
            for sock in reversed(read_sockets):
                try:
                    message = sock.recv(64)
                    message = message.decode(byte_type)
                    msg = ""
                    for char in message:
                        if char in valid_chars:
                            msg += char
                    # get the senders username
                    sender_name = ""  # initializes
                    for player in self.players:
                        if self.players[player] == sock:
                            sender_name = player
                            break
                    if len(msg) > 0:
                        self.process_message(msg, sender_name)
                    else:
                        self.send(sender_name, "Don't send empty messages")
                        break
                except ConnectionResetError:
                    read_sockets.remove(sock)
                    self.disconnect(sock)

    # fill
    def shortcuts(self, msg):
        shortcuts = {
            # random words
            "rbed": "roleblocked",
            # town
            "vig": "Vigilante",
            # mafia
            # coven
            # neutral
            "sk": "Serial Killer",
            "ww": "Werewolf",
            "jest": "Jester",
            "exe": "Executioner",
        }

    # checks message for commands
    def process_message(self, message, sender):
        # if command
        if message[0] == "/":
            words = message.split()
            # dictionary of commands player can send (look in help to update command names)
            list_of_commands = {
                "/w": self.whisper,
                "/v": self.vote,
                "/help": self.help,
                "/guilty": self.guilty,
                "/inno": self.inno,
                self.roles[sender].get_command_phrase(): self.target,
                "/team": self.show_team,
                "/living": self.show_living,
                "/dead": self.show_dead
            }
            for command in list_of_commands:
                if command in words:
                    list_of_commands[command](message, sender)
                    return
            self.send(sender, "That is an invalid command")
            self.help("help", sender)

        # if message
        else:
            self.general_output(message, sender)

    # sends output to everyone who is supposed to get messages from the sender
    def general_output(self, message, sender_name):
        jailor = ""
        # prevents blackmailed from speaking
        if self.roles[sender_name].blackmailed:
            return
        # find  the jailor
        if not self.is_day:
            for player in self.alive_players:
                if self.roles[player].name == "Jailor":
                    jailor = player
                    break

        # processes messages from dead players
        if sender_name in self.dead_players or self.roles[sender_name].name == "Medium":
            # Medium sending message at night
            if self.roles[sender_name].name == "Medium" and sender_name in self.alive_players and not self.is_day:
                # TODO: add seance here
                for player in self.dead_players:
                    self.send(player, f"Medium: {message}")
                self.send(sender_name, f"Medium: {message}")
            else:
                # send messages to Mediums
                if not self.is_day:
                    for player in self.alive_players:
                        if self.roles[player].name == "Medium":
                            self.send(player, f"{sender_name}; {message}")
                for player in self.dead_players:
                    self.send(player, f"{sender_name}: {message}")

        # creates jailor-jailed discussions
        if not self.is_day and len(jailor) > 1 and (sender_name == jailor or self.roles[jailor].jailed == sender_name):
            if sender_name == jailor:
                self.send(self.roles[jailor].jailed, f"Jailor: {message}")
            else:
                self.send(jailor, f"{sender_name}: {message}")

        # mafia chat room
        elif not self.is_day and sender_name in self.mafia_members:
            for maf in self.mafia_members:
                self.send(maf, f"{sender_name}: {message}")

        # coven chat room
        elif not self.is_day and sender_name in self.coven_members:
            for cov in self.coven_members:
                self.send(cov, f"{sender_name}: {message}")

        # vampire chat room
        elif not self.is_day and sender_name in self.vampires:
            for vamp in self.vampires:
                self.send(vamp, f"{sender_name}: {message}")
            # sends to the vampire hunter
            for player in self.players:
                if self.roles[player].name == "Vampire Hunter":
                    self.send(player, f"Vampire: {message}")

        # general day output to everyone
        elif self.is_day and sender_name in self.alive_players:
            self.broadcast(message, sender_name)

    # output the actions of each command
    def help(self, message, sender):
        self.send(sender, "*** Comamands ***")
        command_names = {
            "/help": "print list of help methods",
            "/w": "whisper to someone (ex. /w person hi)",
            "/v": "vote someone up during nomination session",
            "/guilty": "pick guilty during a voting session",
            "/inno": "pick innocent during a voting session",
            "/team": "print friends if you are mafia",
            "/living": "print list of alive players",
            "/dead": "print a list of dead players",
            self.roles[sender].get_command_phrase(): self.roles[sender].command_description
        }
        for command in command_names:
            self.send(sender, f"{command} is used to {command_names[command]}")

    # sends a private message
    def whisper(self, message, sender):
        words = message.split()
        if words[0] != "/w":
            print("whisper passed incorrectly")
            return
        if len(words) < 3:
            return
        target = words[1]
        if target not in self.players:
            print("someone whispered to a non-existent person")
            self.send(sender, "You didn't whisper to a person")
            return
        if sender not in self.alive_players:
            self.send(sender, "Server: dead men tell no tales")
            return
        message = ""
        for word in words[2:]:
            message += word
            message += " "
        for player in self.players:
            if self.roles[player].name == "Blackmailer":
                self.send(player, sender + " whispers: " + message)
        self.broadcast(f"{sender} is whispering to {target}")
        self.send(target, sender + " whispers: " + message)

    # nominate someone for lynching
    def vote(self, message, sender):
        # make sure that it is nomination time
        if not self.nominating:
            print("someone voted before voting period")
            self.send(sender, "It is not voting period")
            return
        # prevent dead votes
        if sender in self.dead_players:
            self.send(sender, "Server: The dead can not vote")
            return
        # remove previous votes
        if sender in self.votes:
            previous_voted = self.votes[sender]
            self.nomination_counts[previous_voted] -= 1
        # find the target
        target = 0
        for player in self.alive_players:
            if player in message:  # allows for character with short name to do weird
                target = player
                break
        # check for GA protection
        if self.roles[target].divine_protection:
            self.broadcast(f"{sender} tried to vote for {target} but failed due to {target}'s divine aid")
            return
        if target == 0:
            self.send(sender, "That is not a valid target")
            return
        self.votes[sender] = target
        if self.roles[sender].name == "Mayor" and self.roles[sender].announced:
            if target in self.nomination_counts:
                self.nomination_counts[target] += 3
            else:
                self.nomination_counts[target] = 3
        else:
            if target in self.nomination_counts:
                self.nomination_counts[target] += 1
            else:
                self.nomination_counts[target] = 1
        self.broadcast(f"{sender} voted against {target}. {target} is now at {self.nomination_counts[target]} votes")

    # vote guilty
    def guilty(self, message, sender):
        # prevents voting before voting time
        if not self.voting:
            self.send(sender, "Server: It is not voting period")
        # prevent accused from voting
        elif sender == self.accused:
            self.send(sender, "Server: The accused can't vote")
        # prevent dead votes
        elif sender in self.dead_players:
            self.send(sender, "Server: The dead can not vote")
        # mayor check
        elif self.roles[sender].name == "Mayor" and self.roles[sender].announced:
            self.votes[sender] = 3
        # normal players
        else:
            self.votes[sender] = 1
        self.broadcast(sender + " has voted")

    # vote innocent
    def inno(self, message, sender):
        # prevents voting before voting time
        if not self.voting:
            self.send(sender, "Server: It is not voting period")
        # prevent accused from voting
        elif sender == self.accused:
            self.send(sender, "Server: The accused can't vote")
        # prevent dead votes
        elif sender in self.dead_players:
            self.send(sender, "Server: The dead can not vote")
        # mayor check
        elif self.roles[sender].name == "Mayor" and self.roles[sender].announced:
            self.votes[sender] = -3
        # normal players
        else:
            self.votes[sender] = -1
        self.broadcast(sender + " has voted")

    # activate your ability towards someone
    def target(self, message, sender):
        Players.main = self
        targets = []
        words = message.strip().split()
        for word in words[1:]:
            targets.append(word)

        self.roles[sender].target(targets)

    # prints other known members of your team (mafia only)
    def show_team(self, message, sender):
        if sender in self.mafia_members:
            self.send(sender, "The players on your team are ...")
            for maf in self.mafia_members:
                self.send(sender, maf)
        elif sender in self.coven_members:
            self.send(sender, "The players on your team are ...")
            for cov in self.coven_members:
                self.send(sender, cov)
        elif sender in self.vampires:
            self.send(sender, "The players on your team are ...")
            for vamp in self.vampires:
                self.send(sender, vamp)

    # print list of everyone who is alive_players
    def show_living(self, msg, sender):
        self.send(sender, "The remaining surviving people are...")
        for player in self.alive_players:
            self.send(sender, player)

    # print list of everyone who is alive_players
    def show_dead(self, msg, sender):
        self.send(sender, "The dead people are...")
        for player in self.dead_players:
            self.send(sender, player)

    # gives necronomicon to Cov leader if possible else random
    def give_necronomicon(self):
        # don't do this if there are no coven in the game
        if len(self.coven_members) == 0: return
        living_coven = []
        cov_leader = 0
        for cov in self.coven_members:
            # check if the player is alive
            if cov in self.alive_players:
                living_coven.append(cov)
                role = self.roles[cov]
                # check that no living player has the necronomicon yet
                if role.has_necronomicon:
                    return
                # check if the conven leader
                if role.name == "Coven Leader":
                    cov_leader = role
                    break
        self.broadcast("The necronomicon has been given to the coven")
        # if the cov leader in dead
        if cov_leader == 0:
            lucky_cov = choice(living_coven)
            self.roles[lucky_cov].has_necronomicon = True
            self.send(lucky_cov, "You have received the necronomicon!")
        # gives to cov_leader
        else:
            cov_leader.has_necronomicon = True
            self.send(cov_leader.username, "You have received the necronomicon!")

    # send message to everyone
    def broadcast(self, msg, sender="Server"):
        for player in self.players:
            # if player == sender: continue
            self.send(player, f"{sender}: {msg}")

    # sends msg to the socket of a given username
    def send(self, name, msg):
        time.sleep(.01)  # to prevent another send before previous is received
        try:
            self.players[name].send(bytes(msg + "\n", byte_type))
        except BrokenPipeError:
            self.disconnect(self.players[name])


game = Game()
if __name__ == "__main__":
    byte_type = "utf-8"
    valid_chars = " abcdefghijklmnopqrstuvwxyz" \
                  + "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                  + "0123456789" \
                  + r"""!"#%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    # use $ for commands
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = '192.168.0.23'
    port = 1234
    s.bind((ip, port))
    s.listen(25)  # the number is the overflow amount

    # countdown times
    countdown = {
        30: "30 seconds remaining",
        10: "10 seconds remaining",
        5: "5 seconds remaining"
    }
    game.play_game()
    print("over")
    s.close()
'''
working:
tracker
escort / consort
SK
LO
Sher
Vamp
Med
WW (double chat message though)
Amne
Mayor
Vig
Disg
Invest
Consig
Witch
Psychic
Executioner
Jester
Jug
Vampire Hunter
Veteran
Framer
Hypnotist
Janitor
Ambushers
Retri
Spy - bug not tested
Crusader
Bodyguard
Doctor
Godfather
Mafioso - conversion not tested
Joker (custom)
survivor
arso
plague / pest
GA

broken:
jailor
trapper 
pirate

TODO:
Coven
    Coven Leader
    Potion Master
    Medusa
    
'''
