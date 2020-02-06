from random import choice
from random import randint

main = None


# todo create conversion into mafioso - hopefully it works
# todo and plunder functionality to other players
# todo - remember for else thing


def rampage(target, kill_msg, attack_strength=3):
    if attack_strength > main.roles[target].tonight_defence:
        kill(target, kill_msg)
    for player in main.alive_players:
        if player == target: continue
        if main.roles[player].targeted == target and attack_strength > main.roles[player].tonight_defence:
            kill(target, kill_msg)


def shuffle_list(original_list):
    new_list = original_list.copy()
    for index in range(len(new_list)):
        original_value = new_list[index]
        rand = randint(0, len(new_list) - 1)
        new_list[index] = new_list[rand]
        new_list[rand] = original_value
    return new_list


def kill(person, means):
    if person in main.alive_players:
        # if someone else already killed that person, day he died in 2 way
        if person in Player.deaths:
            Player.deaths[person] += " and was also " + means
        else:
            Player.deaths[person] = means


class Player:
    # what group they are in
    type = "None"

    # name of the role
    name = "Player"

    # if the player normally return sus to a sheriff
    is_sus = False

    # if it is a unique role
    is_unique = False

    # whether has immunity to escorts and consorts
    immune_to_role_blocks = False

    # normal defence before help
    normal_defence = 0

    # list of valid amounts of targets for this profession
    valid_amount_of_targets = [1]

    # command phrase for this class
    command_phrase = "/target"

    # description of action
    command_description = "activate your role towards the person targeted"

    # list of all people killed that night and how
    deaths = {}

    def __init__(self, username):
        # stores username of the person linked to this object
        self.username = username

        # stores name of the target person (or list of people)
        self.targeted = None

        # targeted list for checking
        self.target_list = None

        # defence after manipulations by other players
        self.tonight_defence = self.normal_defence

        # changes based on framer
        self.tonight_is_sus = self.is_sus

        # changes for disguiser and janitor
        self.tonight_name = self.name

        # death name for Medusa, Janitor, Disguiser
        self.death_name = self.name

        # if in the process of being plundered by the pirate
        self.being_plundered = False

        # there choice of play while being plundered
        self.plunder_choice = "rock"

        # overrides normal targeting limits (used by Necro)
        self.override_targeting = False

        # if been doused by an arso - not used for actual killing but for invest results
        self.doused = False

        # if been hexed by the Hex Master
        self.hexed = False

        # if infected by plague
        self.infected = False

        # if blackmailed for that day
        self.blackmailed = False

        # if protected by the guardian angel
        self.divine_protection = False

    # assigns normal attributes before each person does stuff
    def reset(self):
        self.tonight_defence = self.normal_defence
        self.tonight_is_sus = self.is_sus
        self.death_name = self.name
        self.override_targeting = False
        self.divine_protection = False
        self.targeted = None
        self.target_list = None
        self.blackmailed = False
        self.tonight_name = self.name
        self.plunder_choice = "rock"

    # checks if player can target using their target (target is a list)
    def can_target(self):
        target = self.target_list

        if target is None:
            return False

        if type(target) != list:
            main.broadcast("error")

        if self.username not in main.alive_players and not self.override_targeting:
            return False

        # if target is alive
        for person in target:
            if person not in main.alive_players:
                return False

        # if a valid amount of targets
        if len(target) not in self.valid_amount_of_targets:
            return False

        # if you are role-blocked -- this no work with list
        if target == ["no"]:
            return False

        return True

    # set night target
    def target(self, target):
        self.target_list = target
        if self.can_target():
            if len(target) != 1:
                self.targeted = target
            else:
                self.targeted = target[0]
            main.send(self.username, self.get_target_phrase(self.targeted))
        else:
            main.send(self.username, "You can't do that")

    def winner(self):
        return self.username in main.alive_players

    # return the command for that player
    def get_command_phrase(self):
        return self.command_phrase

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to target {target}"

    # weird stuff
    def activate_target_1(self):
        pass

    # witch and role blocks + coven leader
    def activate_target_2(self):
        pass

    # healing and support role stuff
    def activate_target_3(self):
        pass

    # investigations
    def activate_target_4(self):
        pass

    # killing
    def activate_target_5(self):
        pass

    # role changes and spy
    def activate_target_6(self):
        pass


# ------------------------------------------------------------------

class Townie(Player):
    type = "Town"
    is_sus = False

    def winner(self):
        for player in main.alive_players:
            if main.roles[player].type == "Town":
                return True
        return False


class Sheriff(Townie):
    name = "Sheriff"
    sort = "Investigative"
    command_phrase = "/interrogate"
    command_description = "determine if your target is suspicious"

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to interrogate {target}"

    def activate_target_4(self):
        target = main.roles[self.targeted]
        sus = target.tonight_is_sus
        if sus:
            main.send(self.username, f"{self.targeted} is sus")
        else:
            main.send(self.username, f"{self.targeted} is not sus")


class Investigator(Townie):
    name = "Investigator"
    sort = "Investigative"
    command_phrase = "/investigate"
    command_description = "get list of possible roles for your target"

    invest_results = [
        "Vigilante, Veteran, Mafioso, Pirate, or Ambusher."
        "Medium, Janitor, Retributionist, Necromancer, or Trapper.",
        "Survivor, Vampire Hunter, Amnesiac, Medusa, or Psychic.",
        "Spy, Blackmailer, Jailor, or Guardian Angel.",
        "Sheriff, Executioner, Werewolf, or Poisoner.",
        "Framer, Vampire, Jester, or Hex Master.",
        "Lookout, Forger, Witch, or Coven Leader.",
        "Escort, Transporter, Consort, or Hypnotist.",
        "Doctor, Disguiser, Serial Killer, or Potion Master.",
        "Investigator, Consigliere, Mayor, Tracker, or Plaguebearer.",
        "Bodyguard, Godfather, Arsonist, or Crusader."
    ]

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to investigate {target}"

    def activate_target_4(self):
        target = main.roles[self.targeted]
        if target.doused:
            main.send(self.username, f"{self.targeted} is  a Bodyguard, Godfather, Arsonist, or Crusader.")
        elif target.hexed:
            main.send(self.username, f"{self.targeted} is  a Framer, Vampire, Jester, or Hex Master.")
        else:
            for result in self.invest_results:
                if target.tonight_name in result:
                    main.send(self.username, f"{self.targeted} is  a {result}")
                    return
        main.send(self.username, "Error, could not do that")


class Doctor(Townie):
    name = "Doctor"
    sort = "Protective"
    command_phrase = "/heal"
    command_description = "prevent your target from dying"

    def __init__(self, username):
        super(Doctor, self).__init__(username)
        self.has_self_healed = False

    def can_target(self):
        if super(Doctor, self).can_target():
            # check self target
            if self.targeted == self.username:
                if self.has_self_healed:
                    return False
                self.has_self_healed = True
                return True
            return True
        return False

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to heal {target}"

    def activate_target_2(self):
        target = main.roles[self.targeted]
        target.tonight_defence = 2  # 0- none, 1- normal, 2- strong, 3- super
        target.poisoned = False


class Jailor(Townie):
    name = "Jailor"
    sort = "Killing"
    command_description = "during the day, pick someone to jail. at night decide if you will kill"
    is_unique = True
    valid_amount_of_targets = [0, 1]

    def get_command_phrase(self):
        if main.is_day:
            return "/jail"
        else:
            return ""

    @staticmethod
    def get_target_phrase(target):
        return f"You haul {target} off to jail"

    def __init__(self, username):
        super(Jailor, self).__init__(username)
        self.has_goofed = False  # whether has killed town
        self.jailed = None
        self.is_killing = False

    def reset(self):
        Player.reset(self)
        self.is_killing = False

    def can_target(self):
        target = self.target_list

        if target is None:
            return False

        # if dead
        if self.username not in main.alive_players and not self.override_targeting:
            return False

        # if target is alive
        for person in target:
            if person not in main.dead_players:
                return False

        # if not jailing someone during the day
        if len(target) != 1 and main.is_day:
            return False

        # if has a target when deciding to exe at night
        if len(target) != 0 and not main.is_day:
            return False

        # if you are role-blocked
        if target == "no":
            return False

        return True

    def target(self, target=None):
        # TODO; send decision messages to targeted
        if target is None:
            # if changing mind
            if self.is_killing:
                self.is_killing = False
                main.send(self.username, "You will not be executing")
            # decide to kill
            elif not self.has_goofed:
                self.is_killing = True
                main.send(self.username, "You will be executing")
            else:
                main.send(self.username, "You have goofed, no executions")
        # if this is the day targeting
        else:
            if main.is_day:
                self.jailed = target
                main.send(self.username, f"You are jailing {target} tonight")

    def activate_target_5(self):
        if self.is_killing:
            kill(self.jailed, "deemed unfit to live by the Jailor")
            # prevent actions from inside jail
            main.roles[self.jailed].targeted = None
        else:
            # jailor protection
            main.roles[self.jailed].tonight_defence = 2
        self.jailed = None


class Medium(Townie):
    name = "Medium"
    sort = "Support"
    command_phrase = "/seance"
    command_description = "when dead, chat your target one night"

    def can_target(self):
        target = self.target_list

        if target is None:
            return False

        # if self is alive
        if target is None:
            return False

        if self.username not in main.dead_players:
            return False

        # if target is alive
        for person in target:
            if person not in main.alive_players:
                return False

        # if a valid amount of targets
        if len(target) not in self.valid_amount_of_targets:
            return False

        # if you are role-blocked
        if target == "no":
            return False

        return True


class Escort(Townie):
    name = "Escort"
    sort = "Support"
    command_phrase = "/distract"
    command_description = "prevent your target from acting tonight"
    immune_to_role_blocks = True

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to distract {target}"

    def activate_target_2(self):
        target = main.roles[self.targeted]
        if not target.immune_to_role_blocks:
            target.targeted = "no"


class Lookout(Townie):
    name = "Lookout"
    sort = "Investigative"
    command_phrase = "/watch"
    command_description = "see who visits your target"

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to watch {target}"

    def activate_target_4(self):
        roles = main.roles
        target = main.roles[self.targeted]
        visitors = []
        for role in roles:
            if roles[role].targeted == target.username and role != self.username:
                visitors.append(role)
        main.send(self.username, f"List of visitors: {visitors}")


class Vigilante(Townie):
    name = "Vigilante"
    sort = "Killing"
    command_phrase = "/kill"
    command_description = "kill your target"
    attack_strength = 1

    def can_target(self):
        return super(Vigilante, self).can_target() or main.night_stage == 1

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to shoot {target}"

    def __init__(self, username):
        super().__init__(username)
        self.feels_guilt = False
        self.bullets_left = 3

    # activates if they kill townie
    def activate_target_1(self):
        if self.feels_guilt:
            kill(self.username, "lost to guilt")

    # actual shooting
    def activate_target_5(self):
        roles = main.roles
        target = roles[self.targeted]
        if self.attack_strength > target.tonight_defence and self.bullets_left > 0:
            kill(self.targeted, "shot by a vig")
            if target.type == "Town":
                self.feels_guilt = True
        self.bullets_left -= 1
        main.send(self.username, f"You have {self.bullets_left} remaining")


class Veteran(Townie):
    name = "Veteran"
    sort = "Killing"
    command_phrase = "/alert"
    command_description = "go on alert to kill all visitors"
    is_unique = True
    valid_amount_of_targets = [0]

    def __init__(self, username):
        super(Veteran, self).__init__(username)
        self.shielding = False
        self.alerts = 3

    def can_target(self):
        return self.alerts > 0

    def target(self, target=None):
        if self.shielding or self.alerts == 0:
            self.shielding = False
            main.send(self.username, "You are not on alert")
        else:
            self.shielding = True
            main.send(self.username, "You are on alert")

    def activate_target_1(self):
        if self.shielding:
            self.tonight_defence = 2

    def activate_target_5(self):
        roles = main.roles

        if self.shielding:
            for person in roles:
                if roles[person].targeted == self.username:
                    kill(person, "shot by the veteran")
            self.alerts -= 1
            self.shielding = False


class Retributionist(Townie):
    name = "Retributionist"
    sort = "Support"
    command_phrase = "/revive"
    command_description = "bring a dead player back from the dead"

    def can_target(self):
        target = self.target_list

        if target is None:
            return False

        if self.username not in main.alive_players and not self.override_targeting:
            return False

        # if target is alive
        for person in target:
            if person not in main.dead_players:
                return False

        # if a valid amount of targets
        if len(target) not in self.valid_amount_of_targets:
            return False

        # if you are role-blocked
        if target == "no":
            return False

        return True

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to revive {target}"

    def activate_target_2(self):
        main.alive_players.append(self.targeted)
        main.dead_players.remove(self.targeted)
        main.broadcast(f"{self.targeted} has been brought back to life!")


class Mayor(Townie):
    name = "Mayor"
    sort = "Support"
    command_phrase = "/reveal"
    command_description = "tell the world who you are"
    valid_amount_of_targets = [0]

    def __init__(self, username):
        super(Mayor, self).__init__(username)
        self.announced = False

    def target(self, target=None):
        roles = main.roles
        # broadcast
        for person in roles:
            main.send(person, self.username + " is the Mayor!")
            self.announced = True


class Bodyguard(Townie):
    name = "Bodyguard"
    sort = "Protective"
    command_phrase = "/guard"
    command_description = "put your life on the line to protect someone"
    attack_strength = 2

    @staticmethod
    def get_target_phrase(target):
        return "You have decided to guard " + target

    def __init__(self, username):
        super(Bodyguard, self).__init__(username)
        self.has_vested = False

    def activate_target_3(self):
        # if vesting
        if self.targeted == self.username:
            if self.has_vested:
                main.send(self.username, "You have already vested")
            else:
                self.has_vested = True
                self.tonight_defence = 2
        # if protecting other
        else:
            # check all players for visiting target
            for player in main.players:
                role = main.roles[player]
                if role.targeted == self.targeted:
                    # if attacking
                    if role.command_phrase == "/kill" or role.command_phrase == "/bite":
                        # if has other has higher defence
                        if self.attack_strength > role.tonight_defence:
                            kill(player, "killed by a bodyguard")
                        # check counter attack
                        if role.attack_strength > self.tonight_defence:
                            kill(self.username, 'died protecting someone')
                        break

            # kill or bite


class Crusader(Townie):
    name = "Crusader"
    sort = "Protective"
    command_phrase = "/protect"
    command_description = "protect your target"
    attack_strength = 2

    @staticmethod
    def get_target_phrase(target):
        return "You decide to protect " + target

    # grant protection
    def activate_target_3(self):
        # stops for attempted self protec and invalid targets
        if self.targeted == self.username or self.targeted not in main.alive_players:
            self.targeted = None
            return
        # add strong protection
        main.roles[self.targeted].tonight_defence = 2

        # kill a visitor
        for player in main.alive_players:
            role = main.roles[player]
            if role == self: continue
            if role.targeted == self.targeted and self.attack_strength > role.tonight_defence:
                kill(player, "stabbed by a crusader")
                break


class Psychic(Townie):
    name = "Psychic"
    sort = "Investigative"
    valid_amount_of_targets = [0]
    command_description = "Your action will act automatically"

    def can_target(self):
        return True

    @staticmethod
    def get_target_phrase(target):
        return "Psychics don't target."
        # can this be role-blocked

    def activate_target_4(self):
        shuffled = shuffle_list(main.alive_players)
        if main.day_at % 2 == 0:
            good = None
            # find a good
            for player in shuffled:
                prof = main.roles[player]
                if (prof.type == "Town" or prof.type == "neutral benign") and prof != self:
                    good = prof.username
                    break
            # if Psychic is only town left
            if good is None:
                main.send(self.username, "No other townies are left")
                return
            three_peeps = [good]
            # find 2 more people
            for player in shuffled:
                if len(three_peeps) >= 3:
                    break
                if player != good:
                    three_peeps.append(player)
            # to mix up the order
            three_peeps = shuffle_list(three_peeps)
            main.send(self.username, f"One of these people is good: {three_peeps}")

        else:
            bad = None
            # find a good
            for player in shuffled:
                prof = main.roles[player]
                if prof.type != "Town" and prof.type != "neutral benign":
                    bad = prof.username
                    break
            # if something goes wrong
            if bad is None:
                main.send(self.username, "All bad people are dead")
                return
            three_peeps = [bad]
            # find 2 more people
            for player in shuffled:
                if len(three_peeps) >= 3:
                    break
                if player != bad:
                    three_peeps.append(player)
            # to mix up the order
            three_peeps = shuffle_list(three_peeps)
            main.send(self.username, f"One of these people is good: {three_peeps}")
            # get 2 players, one of which is good


class Spy(Townie):
    name = "Spy"
    sort = "Investigative"
    command_phrase = "/bug"
    command_description = "check what actions happen to your target"

    response = {
        "/kill": "Your target was attacked",
        "/distract": "Your target was role blocked",
        "/trans": "Your target was transported",
        "/heal": "Your target was healed"
    }

    @staticmethod
    def get_target_phrase(target):
        return "You decided to bug " + target

    def activate_target_6(self):
        # get maf visits
        maf_visits = []
        for maf in main.mafia_members:
            visit = main.roles[maf].targeted
            # prevent sending None's and role blocks
            if visit in main.players:
                maf_visits.append(visit)

        # get coven visits
        coven_visits = []
        for cov in main.coven_members:
            visit = main.roles[cov].targeted
            # prevent sending None's and role blocks
            if visit in main.players:
                coven_visits.append(visit)

        # bugging
        bug_info = []
        for player in main.alive_players:
            # ignore self
            if player == self.username:
                continue
            player_role = main.roles[player]
            # checks if they visited
            if player_role.targeted == self.targeted:
                if player_role.command_phrase in self.response:
                    bug_info.append(self.response[player_role.command_phrase])

        main.send(self.username, f"Mafia visits: {maf_visits}, Coven visits: {coven_visits}, Bugging info: {bug_info}")


class Tracker(Townie):
    name = "Tracker"
    sort = "Investigative"
    command_phrase = "/track"
    command_description = "see where your target goes"

    @staticmethod
    def get_target_phrase(target):
        return "You decide to follow " + target

    def activate_target_6(self):  # find a better order
        visited = main.roles[self.targeted].targeted
        if visited is not None and visited != 'no':
            main.send(self.username, f"{self.targeted} visited {visited}")


class Transporter(Townie):
    name = "Transporter"
    sort = "Support"
    command_phrase = "/trans"
    command_description = "switch the position of target 1 and target 2"
    valid_amount_of_targets = [2]

    @staticmethod
    def get_target_phrase(target):
        person_1 = target[0]
        person_2 = target[1]
        return f"You are switching {person_1} and {person_2}"

    def activate_target_1(self):
        person_1 = self.targeted[0]
        person_2 = self.targeted[1]

        # this no work on people with list stuff like witch
        for player in main.alive_players:
            role = main.roles[player]
            if role.targeted == person_1:
                role.targeted = person_2
            elif role.targeted == person_2:
                role.targeted = person_1


class VampireHunter(Townie):
    name = "Vampire Hunter"
    sort = "Killing"
    command_phrase = "/visit"
    command_description = "see if the person you visit is a vampire"

    @staticmethod
    def get_target_phrase(target):
        return "You decide to visit " + target

    def become_vig(self):
        new_role = Vigilante(self.username)
        new_role.bullets_left = 1
        main.roles[self.username] = new_role
        del self

    def activate_target_5(self):
        # checks targeted for being vamp
        if main.roles[self.targeted].name == "Vampire":
            kill(self.targeted, "staked by the vampire hunter")

        # vamp attacking vh will be part of vamp code

        # check if there are vamps left
        is_vamp = False
        for player in main.alive_players:
            if main.roles[player].name == "Vampire":
                is_vamp = True
                break
        if not is_vamp:
            main.send(self.username, "All the vamps are dead. You will now become a Vigilante")
            self.become_vig()


# Trapper
# ------------------------------------------------------------------


class Mafia(Player):
    type = "Mafia"
    kill_phrase = "shot by the mafia"
    is_sus = True

    def __init__(self, username):
        super(Mafia, self).__init__(username)
        main.mafia_members.append(self.username)

    def reset(self):
        super(Mafia, self).reset()
        # a check to see if there is a gf or mafioso
        is_killer = False
        for maf in main.mafia_members:
            if maf in main.alive_players:
                role = main.roles[maf]
                if role.name == "Godfather" or role.name == "Mafioso":
                    is_killer = True
                    break
        # if no killer, become mafioso
        if not is_killer:
            self.become_mafioso()  # will just be promoted to GF immediately

    def winner(self):
        for player in main.alive_players:
            if main.roles[player].type == "Mafia":
                return True
        return False

    # used if there is no mafioso to convert another maf to it
    def become_mafioso(self):
        main.mafia_members.remove(self.username)
        role = Mafioso(self.username)
        main.send(self.username, "You have become the Mafioso!")
        main.roles[self.username] = role
        del self


class Godfather(Mafia):
    name = "Godfather"
    command_phrase = "/kill"
    command_description = "order your mafioso to kill your target, if the mafioso is gone, kill yourself"
    is_sus = False
    is_unique = True
    attack_strength = 1
    normal_defence = 1

    def get_target_phrase(self, target):
        return f"You decided to attack {target}"
        # TODO: add to maf chat room

    # change mafioso target
    def activate_target_3(self):
        target = self.targeted
        self.targeted = None  # to prevent LO when no visit
        mafia = main.mafia_members
        roles = main.roles

        for maf in mafia:
            if roles[maf].name == "Mafioso":
                roles[maf].targeted = target  # check for escort
                return

        # if no Mafioso
        self.targeted = target

    def activate_target_5(self):
        if self.targeted is not None:
            target = main.roles[self.targeted]
            if self.attack_strength > target.tonight_defence:
                kill(target.username, self.kill_phrase)
            else:
                main.send(self.username, "Your targeted resisted your attack")
                main.send(target.username, "You were attacked!")


class Mafioso(Mafia):
    name = "Mafioso"
    command_phrase = "/kill"
    command_description = "kill your target"
    attack_strength = 1

    def reset(self):
        super(Mafioso, self).reset()
        is_gf = False
        for maf in main.mafia_members:
            role = main.roles[maf]
            if role.name == "Godfather":
                is_gf = True
                break
        # if there is no living godfather, become godfather
        if not is_gf:
            self.become_godfather()

    def become_godfather(self):
        main.mafia_members.remove(self.username)
        main.send(self.username, "The Godfather is gone. You have been promoted to Godfather!")
        role = Godfather(self.username)
        main.roles[self.username] = role
        del self

    @staticmethod
    def get_target_phrase(target):
        return f"You voted to attack {target}"

    def activate_target_5(self):
        target = main.roles[self.targeted]
        if self.attack_strength > target.tonight_defence:
            kill(target.username, self.kill_phrase)
        else:
            main.send(self.username, "Your targeted resisted your attack")
            main.send(target.username, "You were attacked!")


class Framer(Mafia):
    name = "Framer"
    sort = "Support"
    command_phrase = "/frame"
    command_description = "make your target look suspicious"

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to frame {target}"

    def activate_target_2(self):
        target = main.roles[self.targeted]
        target.tonight_is_sus = True


class Blackmailer(Mafia):
    name = "Blackmailer"
    sort = "Support"
    command_phrase = "/silence"
    command_description = "prevent your target from speaking"

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to silence {target}"

    def activate_target_2(self):  # maybe adjust when this is done
        main.roles[self.targeted].blackmailed = True


class Consigliere(Mafia):
    name = "Consigliere"
    sort = "Support"
    command_phrase = "/study"
    command_description = "learn the role of your target"

    results = [
        "Your target is a trained protector.They must be a Bodyguard.",
        "Your target is a professional surgeon.They must be a Doctor.",
        "Your target is a beautiful person working for the Town.They must be an Escort.",
        "Your target gathers information about people.They must be an Investigator.",
        "Your target detains people at night.They must be a Jailor.",
        "Your target watches who visits people at night.They must be a Lookout.",
        "Your target is the leader of the Town.They must be the Mayor.",
        "Your target speaks with the dead.They must be a Medium.",
        "Your target wields mystical power.They must be a Retributionist.",
        "Your target is a protector of the Town.They must be a Sheriff.",
        "Your target secretly watches who someone visits.They must be a Spy.",
        "Your target specializes in transportation.They must be a Transporter.",
        "Your target tracks Vampires.They must be a Vampire Hunter!",
        "Your target is a paranoid war hero.They must be a Veteran.",
        "Your target will bend the law to enact justice.They must be a Vigilante.",
        "Your target uses information to silence people.They must be a Blackmailer.",
        "Your target gathers information for the Mafia.They must be a Consigliere.",
        "Your target is a beautiful person working for the Mafia.They must be a Consort.",
        "Your target pretends to be other people.They must be a Disguiser.",
        "Your target is good at forging documents.They must be a Forger.",
        "Your target has a desire to deceive.They must be a Framer!",
        "Your target is the leader of the Mafia.They must be a Godfather.",
        "Your target cleans up dead bodies.They must be a Janitor.",
        "Your target does the Godfather's dirty work. They must be a Mafioso.",
        "Your target does not remember their role.They must be an Amnesiac.",
        "Your target likes to watch things burn.They must be an Arsonist.",
        "Your target wants someone to be lynched at any cost.They must be an Executioner.",
        "Your target wants to be lynched.They must be a Jester.",
        "Your target wants to kill everyone.They must be a Serial Killer.",
        "Your target simply wants to live.They must be a Survivor.",
        "Your target drinks blood.They must be a Vampire!",
        "Your target howls at the moon.They must be a Werewolf.",
        "Your target casts spells on people.They must be a Witch.",
        "Your target is a divine protector.They must be a Crusader.",
        "Your target has the sight.They must be a Psychic.",
        "Your target is skilled in the art of tracking.They must be a Tracker.",
        "Your target is waiting for a big catch.They must be a Trapper.",
        "Your target lies in wait.They must be an Ambusher.",
        "Your target is skilled at disrupting others.They must be a Hypnotist.",
        "Your target is watching over someone. They must be a Guardian Angel.",
        "Your target gets more powerful with each kill.They must be a Juggernaut.",
        "Your target reeks of disease.They must be Pestilence, Horseman of the Apocalypse.",
        "Your target wants to plunder the Town.They must be a Pirate.",
        "Your target is a carrier of disease.They must be the Plaguebearer.",
        "Your target leads the mystical.They must be a Coven Leader.",
        "Your target is versed in the ways of hexes.They must be the Hex Master.",
        "Your target has a gaze of stone.They must be Medusa.",
        "Your target uses the deceased to do their dirty work.They must be the Necromancer.",
        "Your target uses herbs and plants to kill their victims.They must be the Poisoner.",
        "Your target works with alchemy.They must be a Potion Master."
    ]

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to study {target}"

    def activate_target_4(self):
        role = main.roles[self.targeted]
        for result in self.results:
            if role.tonight_name in result:
                main.send(self.username, result)
                break


class Consort(Mafia):
    name = "Consort"
    sort = "Support"
    command_phrase = "/distract"
    command_description = "prevent your target from acting"
    immune_to_role_blocks = True

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to distract {target}"

    def activate_target_2(self):
        roles = main.roles
        target = roles[self.targeted]
        if not target.immune_to_role_blocks:
            target.targeted = "no"


class Disguiser(Mafia):
    name = "Disguiser"
    sort = "Deception"
    command_phrase = "/disguise"
    command_description = "pretend to be like your target"

    @staticmethod
    def get_target_phrase(target):
        return "You decide to pretend to be like " + target

    def activate_target_2(self):
        self.tonight_name = main.roles[self.targeted].name
        self.death_name = main.roles[self.targeted].name


class Janitor(Mafia):
    name = "Janitor"
    sort = "Deception"
    command_phrase = "/clean"
    command_description = "clean up a murder"

    @staticmethod
    def get_target_phrase(target):
        return "You decide to clean " + target

    def __init__(self, username):
        super(Janitor, self).__init__(username)
        self.cleans = 3

    def activate_target_2(self):
        if self.cleans > 0:
            main.roles[self.targeted].death_name = "Cleaned"


class Ambusher(Mafia):
    # this is similar to Crusader
    name = "Ambusher"
    sort = "Killing"
    command_phrase = "/ambush"
    command_description = "kill a visitor of your target"
    kill_phrase = "ambushed in the night"
    attack_strength = 1

    @staticmethod
    def get_target_phrase(target):
        return f"You decide lie in wait at {target}'s house"

    def activate_target_1(self):
        has_ambushed = False
        for player in shuffle_list(main.alive_players):
            target = main.roles[player]
            if target.type == "Mafia":  # doesn't kill mafia members
                continue
            if target.targeted == self.targeted:
                # send messages to all others
                if has_ambushed:
                    main.send(player, self.username + " was waiting in ambush here tonight")
                else:
                    if self.attack_strength > target.tonight_defence:
                        kill(target.username, self.kill_phrase)
                    else:
                        main.send(self.username, "Your targeted resisted your attack")
                        main.send(target.username, "You were attacked!")
                    has_ambushed = True


class Hypnotist(Mafia):
    name = "Hypnotist"
    sort = "Deception"
    command_phrase = "/confuse"
    command_description = "send your target a random message"

    @staticmethod
    def get_target_phrase(target):
        return "You decide to confuse " + target

    messages = [
        "You were transported to another location.",
        "Someone occupied your night. You were role blocked!",
        "You were attacked but someone fought off your attacker!",
        "You were attacked but someone nursed you back to health!",
        "You feel a mystical power dominating you. You were controlled by a Witch!",
        "You were poisoned. You will die tomorrow!",
        "You were attacked but someone protected you!",
        "You were poisoned but someone nursed you back to health!",
        "Someone tried to poison you but someone fought off your attacker!",
        "You triggered a trap!",
        "You were attacked but a trap saved you!",
        "A trap attacked you but someone nursed you back to health!"
    ]

    def activate_target_2(self):
        main.send(self.targeted, choice(self.messages))


# ------------------------------------------------------------------


class SerialKiller(Player):
    type = "neutral killing"
    name = "Serial Killer"
    command_phrase = "/kill"
    command_description = "kill the target"
    is_sus = True
    attack_strength = 1
    normal_defence = 1
    kill_phrase = "stabbed by the Serial killer"

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to murder {target}"

    def can_target(self):
        target = self.target_list

        if target is None:
            return False

        # if this not first day after death
        if self.username not in main.alive_players and not self.override_targeting:
            return False

        # if target is alive
        for person in target:
            if person not in main.alive_players:
                return False

        # if a valid amount of targets
        if len(target) not in self.valid_amount_of_targets:
            return False

        return True

    def activate_target_5(self):
        roles = main.roles
        if self.targeted == "no":  # kill escort/Jailor if rbed
            for person in roles:
                if roles[person].name in ("Escort", "Jailor") and roles[person].targeted == self.username:
                    if self.attack_strength > roles[person].tonight_defence:
                        kill(person, self.kill_phrase)
        else:
            if self.attack_strength > roles[self.targeted].tonight_defence:
                kill(self.targeted, self.kill_phrase)


class Jester(Player):
    type = "neutral evil"
    name = "Jester"
    command_phrase = "/haunt"
    command_description = "kill target"
    valid_amount_of_targets = [1]
    haunt_strength = 3

    @staticmethod
    def get_target_phrase(target):
        return "You decide to haunt " + target

    # initializes has_won
    def __init__(self, username):
        super(Jester, self).__init__(username)
        self.has_won = False
        self.day_i_died = -1

    def can_target(self):
        target = self.target_list

        if target is None:
            return False

        # if this not first day after death
        if self.username not in main.dead_players or main.day_at != self.day_i_died + 1:
            return False

        # if target is alive
        for person in target:
            if person not in main.alive_players:
                return False

        # if a valid amount of targets
        if len(target) not in self.valid_amount_of_targets:
            return False

        # if you are role-blocked
        if target == "no":
            return False

        return True

    # is_won is made true in the lynch method in Host.py
    def winner(self):
        return self.has_won

    # haunt
    def activate_target_1(self):
        if self.haunt_strength > main.roles[self.targeted].tonight_defence:
            kill(self.targeted, "haunted from guilt")


class Executioner(Player):
    type = "neutral evil"
    name = "Executioner"
    command_description = " do nothing"
    normal_defence = 1
    valid_amount_of_targets = [0]

    def get_command_phrase(self):
        return "You can't target"

    def can_target(self):
        return True

    # normal plus assign target
    def __init__(self, username):
        super(Executioner, self).__init__(username)
        self.has_won = False
        self.my_target = None
        if main.day_at != 0:
            self.assign_target()

    # assigning town target
    def assign_target(self):
        list_of_players = shuffle_list(main.alive_players)
        has_assigned = False
        for player in list_of_players:
            if main.roles[player].type == "Town":
                self.my_target = player
                has_assigned = True
                break
        if has_assigned:
            main.send(self.username, "Your target is " + self.my_target)
        else:  # should never happen
            main.send(self.username, "something broke")

    # change into a jester
    def become_jester(self):
        role = Jester(self.username)
        main.roles[self.username] = role
        del self

    def winner(self):
        return self.has_won

    # check to change at the end of the night
    def activate_target_6(self):
        if not self.has_won and self.my_target not in main.alive_players:
            main.send(self.username, "Your target is dead. You are now a jester")
            self.become_jester()
        print(main.alive_players)


class Survivor(Player):
    type = "neutral benign"
    name = "Survivor"
    command_phrase = "/vest"
    command_description = "protect yourself"
    valid_amount_of_targets = [0]

    def can_target(self):
        return self.vests_remaining > 0 and self.username in main.alive_players

    def __init__(self, username):
        super(Survivor, self).__init__(username)
        self.vests_remaining = 4
        self.vesting = False

    def target(self, target):
        if self.vesting:
            main.send(self.username, "You decided not to vest")
            self.vesting = False
        elif self.vests_remaining > 0:
            main.send(self.username, "You decided to vest")
            self.vesting = True
        else:
            main.send(self.username, "You are out of vests")

    def activate_target_3(self):
        if self.vesting:
            self.tonight_defence = 1  # basic defence
            self.vests_remaining -= 1
            main.send(self.username, f"You have {self.vests_remaining} vest remaining")
        self.vesting = False


class Witch(Player):
    type = "neutral evil"
    name = "Witch"
    command_phrase = "/control"
    command_description = "send target 1 to target 2"
    valid_amount_of_targets = [2]
    immune_to_role_blocks = True
    is_sus = True

    results = [
        "Your target is a trained protector.They must be a Bodyguard.",
        "Your target is a professional surgeon.They must be a Doctor.",
        "Your target is a beautiful person working for the Town.They must be an Escort.",
        "Your target gathers information about people.They must be an Investigator.",
        "Your target detains people at night.They must be a Jailor.",
        "Your target watches who visits people at night.They must be a Lookout.",
        "Your target is the leader of the Town.They must be the Mayor.",
        "Your target speaks with the dead.They must be a Medium.",
        "Your target wields mystical power.They must be a Retributionist.",
        "Your target is a protector of the Town.They must be a Sheriff.",
        "Your target secretly watches who someone visits.They must be a Spy.",
        "Your target specializes in transportation.They must be a Transporter.",
        "Your target tracks Vampires.They must be a Vampire Hunter!",
        "Your target is a paranoid war hero.They must be a Veteran.",
        "Your target will bend the law to enact justice.They must be a Vigilante.",
        "Your target uses information to silence people.They must be a Blackmailer.",
        "Your target gathers information for the Mafia.They must be a Consigliere.",
        "Your target is a beautiful person working for the Mafia.They must be a Consort.",
        "Your target pretends to be other people.They must be a Disguiser.",
        "Your target is good at forging documents.They must be a Forger.",
        "Your target has a desire to deceive.They must be a Framer!",
        "Your target is the leader of the Mafia.They must be a Godfather.",
        "Your target cleans up dead bodies.They must be a Janitor.",
        "Your target does the Godfather's dirty work. They must be a Mafioso.",
        "Your target does not remember their role.They must be an Amnesiac.",
        "Your target likes to watch things burn.They must be an Arsonist.",
        "Your target wants someone to be lynched at any cost.They must be an Executioner.",
        "Your target wants to be lynched.They must be a Jester.",
        "Your target wants to kill everyone.They must be a Serial Killer.",
        "Your target simply wants to live.They must be a Survivor.",
        "Your target drinks blood.They must be a Vampire!",
        "Your target howls at the moon.They must be a Werewolf.",
        "Your target casts spells on people.They must be a Witch.",
        "Your target is a divine protector.They must be a Crusader.",
        "Your target has the sight.They must be a Psychic.",
        "Your target is skilled in the art of tracking.They must be a Tracker.",
        "Your target is waiting for a big catch.They must be a Trapper.",
        "Your target lies in wait.They must be an Ambusher.",
        "Your target is skilled at disrupting others.They must be a Hypnotist.",
        "Your target is watching over someone. They must be a Guardian Angel.",
        "Your target gets more powerful with each kill.They must be a Juggernaut.",
        "Your target reeks of disease.They must be Pestilence, Horseman of the Apocalypse.",
        "Your target wants to plunder the Town.They must be a Pirate.",
        "Your target is a carrier of disease.They must be the Plaguebearer.",
        "Your target leads the mystical.They must be a Coven Leader.",
        "Your target is versed in the ways of hexes.They must be the Hex Master.",
        "Your target has a gaze of stone.They must be Medusa.",
        "Your target uses the deceased to do their dirty work.They must be the Necromancer.",
        "Your target uses herbs and plants to kill their victims.They must be the Poisoner.",
        "Your target works with alchemy.They must be a Potion Master."
    ]

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to control {target[0]} to {target[1]}"

    def __init__(self, username):
        super(Witch, self).__init__(username)
        self.has_sheild = True  # TODO: find a way to add this functionality

    def activate_target_2(self):
        person_1 = self.targeted[0]
        person_2 = self.targeted[1]

        role = main.roles[person_1]
        role.targeted = person_2
        main.send(person_1, "You were witched")

        for result in self.results:
            if role.tonight_name in result:
                main.send(self.username, result)
                break


class Vampire(Player):
    type = "neutral chaos"
    name = "Vampire"
    command_phrase = "/bite"
    command_description = "vote to convert or kill your target"
    kill_phrase = "bitten by a Vampire"
    is_sus = True
    attack_strength = 1

    # if true they can't bite tonight
    previous_bite = -5
    # class variable for counting votes
    votes = {}

    def __init__(self, username):
        super(Vampire, self).__init__(username)
        main.vampires.append(self.username)

    @staticmethod
    def get_target_phrase(target):
        return f"You voted to bite {target}"

    @staticmethod
    def bite(target):
        role = main.roles[target]
        main.roles[target] = Vampire(target)
        Vampire.username = target
        del role
        main.send(target, "You have been bitten by a Vampire. You are now a vampire")

    # check if bit last night
    def can_bite(self):
        return main.day_at - self.previous_bite > 1

    def can_target(self):
        return Player.can_target(self) and self.can_bite()

    def target(self, target):
        super(Vampire, self).target(target)
        for vamp in main.vampires:
            main.send(vamp, f"{self.username} has voted to bite {self.targeted}")

    def winner(self):
        for player in main.alive_players:
            if main.roles[player].type == "Vampire":
                return True
        return False

    def reset(self):
        super(Vampire, self).reset()
        self.votes = {}

    # voting
    def activate_target_4(self):
        if self.targeted in self.votes:
            self.votes[self.targeted] += 1
        else:
            self.votes[self.targeted] = 1

    # biting
    def activate_target_5(self):
        # if youngest vampire
        if self.username == main.vampires[-1] and self.can_bite():
            # find most popular
            top_count = 0
            top_target = None
            for vote in self.votes:
                if self.votes[vote] > top_count:
                    top_count = self.votes[vote]
                    top_target = vote
            if top_target is None or top_count == 0:
                return
            role = main.roles[top_target]
            # check for vh
            if role.name == "Vampire Hunter":
                kill(self.username, "staked by the Vampire Hunter")
                main.send(top_target, "The vampires visited you last night")
            # checks if cannot convert : unique, maf, coven, too many vamps
            elif role.is_unique or role.type == "Mafia" or role.type == "Coven" or len(main.vampires) >= 4:
                if self.attack_strength > role.tonight_defence:
                    kill(role.username, self.kill_phrase)
                else:
                    main.send(self.username, "Your targeted resisted your attack")
                    main.send(role.username, "You were attacked!")
            # check target defence
            elif self.attack_strength > role.tonight_defence:
                self.bite(top_target)
                self.previous_bite = main.day_at


class Arsonist(Player):
    type = "neutral killing"
    name = "Arsonist"
    command_phrase = "/douse"  # todo find a way to also have ignite
    command_description = "douse your target or if target is yourself, kill all doused"
    kill_phrase = "burned by an arsonist"
    normal_defence = 1
    attack_strength = 3

    # should the amount of targets be 0 and 1?

    @staticmethod
    def get_target_phrase(target):
        return "You decide to douse " + target

    def __init__(self, username):
        super(Arsonist, self).__init__(username)
        self.doused = []
        self.burning = False

    def can_target(self):
        return super(Arsonist, self).can_target() or main.night_stage == 5

    def target(self, target):
        self.target_list = target
        if self.can_target():
            # igniting
            if len(target) == 0 or target == [self.username]:
                self.targeted = None
                self.burning = True
                main.send(self.username, "You are igniting")
            # dousing
            else:
                self.targeted = target[0]
                self.burning = False
                main.send(self.username, "You are dousing " + self.targeted)

    # dousing
    def activate_target_3(self):
        if self.targeted not in self.doused and self.targeted is not None:
            self.doused.append(self.targeted)
            main.roles[self.targeted].doused = True

    # igniting
    def activate_target_5(self):
        if self.burning:
            for doused in self.doused:
                if doused in main.alive_players and self.attack_strength > main.roles[doused].tonight_defence:
                    kill(doused, self.kill_phrase)


class Werewolf(Player):
    type = "neutral killing"
    name = "Werewolf"
    command_phrase = "/kill"
    command_description = "rampage at your target's house, but only on full moons"
    kill_phrase = "mauled by a Werewolf"
    normal_defence = 1

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to maul {target}"

    def activate_target_5(self):
        if main.day_at % 2 == 0:
            rampage(self.targeted, self.kill_phrase)


class Amnesiac(Player):
    type = "neutral benign"
    name = "Amnesiac"
    command_phrase = "/remember"
    command_description = "make your role like a dead player"

    @staticmethod
    def get_target_phrase(target):
        return "You decided to remember to be like " + target

    def winner(self):
        return False

    def can_target(self):
        target = self.target_list

        if target is None:
            return False

        if self.username not in main.alive_players and not self.override_targeting:
            return False

        # if target is alive
        for person in target:
            if person not in main.dead_players:
                return False

        # if a valid amount of targets
        if len(target) not in self.valid_amount_of_targets:
            return False

        # if you are role-blocked
        if target == "no":
            return False

        return True

    def activate_target_6(self):
        targeted_role = type(main.roles[self.targeted])
        role = targeted_role(self.username)
        main.roles[self.username] = role
        main.send(self.username, f"You have become a {targeted_role.name}")
        del self


class GuardianAngel(Player):
    type = "neutral benign"
    name = "Guardian Angel"
    command_phrase = "/protect"
    command_description = "grant divine protection to your friend (no target)"
    valid_amount_of_targets = [0]
    astral = True

    def __init__(self, username):
        super(GuardianAngel, self).__init__(username)
        self.heals_remaining = 2
        targets = main.alive_players.copy()
        targets.remove(username)
        target = choice(targets)  # prevent certain types
        self.my_target = target
        main.send(self.username, "Your target is " + target)

    def winner(self):
        return self.my_target in main.alive_players

    def can_target(self):
        return True

    # if target dies
    def become_survivor(self):
        new_role = Survivor(self.username)
        new_role.vests_remaining = 0
        main.roles[self.username] = new_role
        del self

    def heal(self):
        # remove dousing
        if self.target_role.doused:
            self.target_role.doused = False
            for player in main.alive_players:
                role = main.roles[player]
                if role.name == "Arsonist" and self.my_target in role.doused:
                    role.doused.remove(self.my_target)
        # remove Coven's poison
        self.target_role.poisoned = False

        # remove infection
        self.target_role.infected = False

        # remove hex
        self.target_role.hexed = False

        # enable a voting immunity
        self.target_role.divine_protection = True

        # send message
        main.broadcast(f"A Guardian Angel protected {self.my_target}")
        self.heals_remaining -= 1

    def target(self, target=None):
        if self.targeted is None or not self.targeted:
            self.targeted = True
            main.send(self.username, "You have decided to protect tonight")
        else:
            self.targeted = False
            main.send(self.username, "You have decided not to protect tonight")

    # this level if dead
    def activate_target_1(self):
        self.target_role = main.roles[self.my_target]
        if self.username in main.dead_players and self.targeted:
            if self.heals_remaining > 0:
                self.heal()
            else:
                main.send(self.username, "You have no heals left")

    # this level if alive
    def activate_target_3(self):
        self.target_role = main.roles[self.my_target]
        if self.username in main.alive_players and self.targeted:
            if self.heals_remaining > 0:
                self.heal()
            else:
                main.send(self.username, "You have no heals left")
        elif self.username in main.dead_players:
            main.send("Your target has died. You will now become a Survivor.")
            self.become_survivor()


class Juggernaut(Player):
    type = "neutral killing"
    name = "Juggernaut"
    command_phrase = "/kill"
    command_description = "kill your target, result may increase as the game progresses"
    kill_phrase = "massacred by a juggernaut"

    @staticmethod
    def get_target_phrase(target):
        return "You decided to massacre " + target

    def __init__(self, username):
        super(Juggernaut, self).__init__(username)
        self.amount_of_kills = 0
        self.attack_strength = 2  # powerful
        self.normal_defence = 0  # none to start

    def kill(self, target):
        if self.amount_of_kills == 0:
            # full moon
            if main.day_at % 2 == 0 and self.attack_strength > main.roles[target].tonight_defence:
                kill(target, self.kill_phrase)
                self.level_up()
            elif self.attack_strength <= main.roles[target].tonight_defence:
                main.send(self.username, "They resisted you attack")
            else:
                main.send(self.username, "Until you level up, you can only attack on full moons")
        elif self.amount_of_kills <= 2:
            if self.attack_strength > main.roles[target].tonight_defence:
                kill(target, self.kill_phrase)
                self.level_up()
            else:
                main.send(self.username, "They resisted you attack")
        else:
            if self.attack_strength > main.roles[target].tonight_defence:
                rampage(target, self.kill_phrase, self.attack_strength)
                self.level_up()
            else:
                main.send(self.username, "They resisted you attack")

    def level_up(self):
        if self.amount_of_kills == 0:
            main.send(self.username, "You leveled up! You can now attack every night!")
        elif self.amount_of_kills == 1:
            main.send(self.username, "You leveled up! You have gained a basic defence!")
            self.normal_defence = 1
        elif self.amount_of_kills == 2:
            main.send(self.username, "You leveled up! You will now rampage!")
        elif self.amount_of_kills == 3:
            main.send(self.username, "You reached your max level! You now deal Unstoppable attacks!")
            self.attack_strength = 3
        else:
            main.send(self.username, "Keep up the good work")
        self.amount_of_kills += 1

    def activate_target_5(self):
        self.kill(self.targeted)


class PlagueBearer(Player):
    is_unique = True
    type = "neutral chaos"
    name = "Plague Bearer"
    command_phrase = "/infect"
    command_description = "infect your target, when everyone is infected you will become Pestilence"

    @staticmethod
    def get_target_phrase(target):
        return "You decided to infect " + target

    def can_target(self):
        return super(PlagueBearer, self).can_target() or main.night_stage == 6  # can always check to be pest

    # at the lynched was only uninfected
    def reset(self):
        super(PlagueBearer, self).reset()
        self.infected = True
        # check at the beginnging of the night
        is_uninfected = False
        for player in main.alive_players:
            if not main.roles[player].infected:
                is_uninfected = True
                break
        if not is_uninfected:
            self.become_pestilence()
            main.broadcast("The Pestilence has arisen!")

    def become_pestilence(self):
        new_role = Pestilence(self.username)
        main.roles[self.username] = new_role
        del self

    def activate_target_5(self):
        # infect everyone
        for player in main.alive_players:
            role = main.roles[player]
            # infect everyone the infected visit
            if role.infected:
                main.roles[role.targeted].infected = True
            # infect everyone the visit infected
            elif role.targeted in main.roles and main.roles[role.targeted].infected:
                role.infected = True

    # check if Plague Bearer can change into Pest
    def activate_target_6(self):
        print("test")
        is_uninfected = False
        for player in main.alive_players:
            if not main.roles[player].infected:
                is_uninfected = True
                break
        if not is_uninfected:
            print("nerd")
            main.broadcast("The Pestilence has arisen!")
            self.become_pestilence()


class Pestilence(Player):
    is_unique = True
    type = "neutral chaos"
    name = "Pestilence"
    command_phrase = "/kill"
    command_description = "massacre everyone at your target's house"
    attack_strength = 2  # strong
    normal_defence = 4  # unstoppable

    def reset(self):
        super(Pestilence, self).reset()
        self.tonight_name = PlagueBearer.name

    @staticmethod
    def get_target_phrase(target):
        return f"You decided to eradicate {target}"

    def activate_target_5(self):
        rampage(self.targeted, "obliterated by Pestilence, Horseman of the Apocalypse", self.attack_strength)


class Pirate(Player):
    type = "neutral chaos"
    name = "Pirate"
    command_phrase = "/plunder"
    command_description = "plunder 2 players to win. pluder by doing /plunder (target) rock/paper/scissors"
    attack_strength = 2
    kill_phrase = "killed by a pirate"
    valid_amount_of_targets = [2]
    # play: beats
    plays = {"rock": "scissors", "paper": "rock", "scissors": "rock"}

    def __init__(self, username):
        super(Pirate, self).__init__(username)
        # amount of successful plunders
        self.plunders = 0
        self.victim = None
        self.action = None

    def can_target(self):
        if main.night_stage in [5, 6]:  # 5 is kill, 6 is undo being plundered
            return True

        if len(self.target_list) not in self.valid_amount_of_targets:
            return False

        target = self.target_list[0]
        action = self.target_list[1]

        # can only act when alive
        if self.username not in main.alive_players or self.override_targeting:
            return False

        # target must be alive
        if target not in main.alive_players:
            return False

        # must be rock, paper, or scissors
        if action not in self.plays:
            return False

        return main.is_day

    def target(self, target):
        self.target_list = target
        if self.can_target():
            main.roles[target[0]].being_plundered = True
            self.victim, self.action = target[0], target[1]

    def activate_target_5(self):
        if self.victim is not None:
            # test to see if i win
            role = main.roles[self.victim]
            can_plunder = self.plays[self.action] == role.plunder_choice
            # if you won
            if can_plunder:
                self.plunders += 1
                main.send(self.username, "Your plunder yielding rich booty!")
                if self.attack_strength > role.tonight_defence:
                    kill(role.username, self.kill_phrase)
                else:
                    main.send(self.username, "Your targeted resisted your attack")
                    main.send(role.username, "You were attacked!")
            else:
                main.send(self.username, "Your plunder failed!")

    # reset
    def activate_target_6(self):
        if self.victim is not None:
            role = main.roles[self.victim]
            role.being_plundered = False
            self.victim = None
            self.action = None

    def winner(self):
        return self.plunders >= 2


# sorcerer


# ------------------------------------------------------------------
class Coven(Player):
    type = "Coven"
    is_sus = True
    necronomicon = False
    is_unique = True

    def __init__(self, username):
        super(Coven, self).__init__(username)
        main.coven_members.append(self.username)
        self.is_sus = True
        self.has_necronomicon = False

    def winner(self):
        for player in main.alive_players:
            if main.roles[player].type == "Coven":
                return True
        return False


class CovenLeader(Coven, Witch):
    name = "Coven Leader"
    attack_strength = 1
    kill_phrase = "was killed by a Coven Leader"

    # necronomicon attack
    def activate_target_5(self):
        if self.has_necronomicon:
            if self.attack_strength > main.roles[self.targeted[0]].tonight_defence:
                kill(self.targeted[0], self.kill_phrase)
            else:
                main.send(self.username, "Your targeted resisted your attack")
                main.send(self.targeted[0], "You were attacked!")


class HexMaster(Coven):
    name = "Hex Master"
    command_phrase = "/hex"
    command_description = "hex target, if all enemies are hexed, they will all die"
    kill_phrase = "hexed"
    basic_attack_strength = 1
    final_hex_strength = 3

    def activate_target_3(self):
        target = main.roles[self.targeted]
        # hexing target
        target.hexed = True

        # if necronomicon also deals basic attack
        if self.necronomicon:  # todo make astral
            if self.basic_attack_strength > main.roles[self.targeted[0]].tonight_defence:
                kill(self.targeted[0], self.kill_phrase)
            else:
                main.send(self.username, "Your targeted resisted your attack")
                main.send(self.targeted[0], "You were attacked!")

        # check if all enemies are hexed
        all_hexed = True
        for player in main.alive_players:
            role = main.roles[player]
            if role.type != "Coven" and not role.hexed:
                all_hexed = False
                break
        # if all hexed, kill all the hexed
        if all_hexed:
            for player in main.alive_players:
                role = main.roles[player]
                if role.hexed and self.final_hex_strength > role.tonight_defence:
                    kill(player, self.kill_phrase)


class Medusa(Coven):
    name = "Medusa"
    command_phrase = "/gaze"
    kill_phrase = "turned to stone by a Medusa"
    command_description = "rampage at your targets house and turn them to stone"
    gazes_remaining = 3

    def activate_target_3(self):
        if self.gazes_remaining > 0 or self.necronomicon:
            for player in main.alive_players:
                role = main.roles[player]
                if role.targeted == self.targeted and player != self.username:
                    role.death_name = "Stoned"
            rampage(self.targeted, self.kill_phrase, 3)
        else:
            main.send(self.username, "You have no gazes remaining")


class Necromancer(CovenLeader):
    name = "Necromancer"
    command_description = "control a dead player to one of the living"
    # already used dead
    rotten_corpses = []
    # todo: add necronomicon

    def can_target(self):
        target = self.target_list

        if target is None:
            return False

        if type(target) != list:
            main.broadcast("error")

        if self.username not in main.alive_players and not self.override_targeting:
            return False

        # if a valid amount of targets
        if len(target) not in self.valid_amount_of_targets:
            return False

        # if first player alive
        if target[0] not in main.alive_players:
            return False

        # if second player valid corpse
        if target[1] not in main.dead_players or target[1] in self.rotten_corpses:
            return False

        # if you are role-blocked -- this no work with list
        if target == ["no"]:
            return False

        return True

    def activate_target_1(self):
        corpse = self.targeted[0]
        target = self.targeted[1]

        # prevent reuse
        self.rotten_corpses.append(corpse)

        role = main.roles[corpse]
        role.targeted = target
        role.override_target = True


class Poisoner(Coven):
    name = "Poisoner"
    command_phrase = "/poison"
    kill_phrase = "died to poison"
    # append to this when you get necronomicon
    super_poisoned = []

    def activate_target_5(self):
        # kill poisoned
        for player in main.alive_players:
            role = main.players[player]
            if role.poisoned or player in self.super_poisoned:
                kill(player, self.kill_phrase)


        # poison the one you visit
        main.roles[self.targeted].infected = True
        if self.has_necronomicon:
            self.super_poisoned.append(self.targeted)
        main.send(self.targeted, "You have been poisoned")


class PotionMaster(Coven):  # with necro there is no cooldown
    name = "Potion Master"
    command_description = "write /target name and then type of targeting; heal, reveal, or kill. " \
                          "3 day delay to reuse the same ability"
    command_phrase = ""
    attack_strength = 1
    kill_phrase = "died to a skilled Potion Master"
    valid_amount_of_targets = [2]
    # list of abilities and boolean of if able to use
    previous_use = {"heal": -3, "reveal": -3, "kill": -3}

    def can_target(self):
        # can length
        if len(self.target_list) != 2:
            return False

        # if one of the three action types
        if self.target_list[1] not in self.previous_use:
            return False

        if main.day_at - self.previous_use[self.target_list[1]] > 2 or self.has_necronomicon:
            return False

        return super(PotionMaster, self).can_target()  # this won't work

    # heals
    def activate_target_3(self):
        target = main.roles[self.targeted[0]]
        action = self.targeted[1]
        if action == "heal":
            target.tonight_defence = 2
            target.poisoned = False
            self.previous_use[action] = main.day_at

    # investigate - basically Consig
    def activate_target_4(self):
        results = Consigliere.results
        target = main.roles[self.targeted[0]]
        action = self.targeted[1]
        if action == "reveal":
            for result in results:
                if target.name in result:
                    main.send(self.username, result)
                    break
            self.previous_use[action] = main.day_at

    # kill
    def activate_target_5(self):
        target = main.roles[self.targeted[0]]
        action = self.targeted[1]
        if action == "kill":
            if self.attack_strength > target.tonight_defence:
                kill(target.username, self.kill_phrase)
            else:
                main.send(self.username, "Your targeted resisted your attack")
                main.send(target.username, "You were attacked!")


# ------------------------------------------------------------------
class Joker(Player):
    name = "Joker"
    command_phrase = "/sudo"
    command_description = "/sudo target will broadcast a message as if it where the player"

    def __init__(self, username):
        super(Joker, self).__init__(username)
        self.has_won = False

    def winner(self):
        return self.has_won

    def can_target(self):
        target = self.target_list

        if target is None:
            return False

        # check length
        if len(target) <= 1:
            return False

        # can only sudo at day
        if not main.is_day:
            return False

        return target[0] in main.alive_players

    def target(self, target):
        self.target_list = target
        if self.can_target():
            sudoed = target[0]
            msg = " ".join(target[1:])
            main.general_output(msg, sudoed)

# add more horseman of the apocalypse

# Soldier / War
# Famine
# Death


def random_town():
    global town, all_roles
    role = choice(town)
    if role.is_unique:
        town.remove(role)
        all_roles.remove(role)
    return role


def random_role():
    global all_roles
    role = choice(all_roles)
    if role.is_unique:
        all_roles.remove(role)
    return role


# assign roles - classic mode
def assign_role(name):
    global game_players
    if len(game_players) > 0:
        prof = choice(game_players)
        game_players.remove(prof)
    else:
        prof = random_role()
    return prof(name)


town = [
    Sheriff, Investigator, Spy, Psychic, Lookout, Tracker,  # investigator
    VampireHunter, Vigilante, Veteran, Jailor,  # killing
    Mayor, Retributionist, Escort, Medium, Retributionist, Transporter,  # support
    Doctor, Crusader, Bodyguard  # protective
]

mafia = [
    Godfather, Mafioso, Ambusher,  # killing
    Janitor, Consort, Consigliere,  # support
    Disguiser, Hypnotist, Framer  # deception
]

coven = [CovenLeader, HexMaster, Medusa, Necromancer, Poisoner, PotionMaster]

neutral = [
    Amnesiac, Survivor, GuardianAngel,  # benign
    Jester, Executioner, Witch,  # evil
    Vampire, Pirate, PlagueBearer,  # chaos - also Pestilence
    Werewolf, Arsonist, Juggernaut, SerialKiller  # killing
]

all_roles = []  # creates the list
all_roles.extend(town)  # add town
all_roles.extend(mafia)  # add maf
# all_roles.extend(coven)  # add cov
all_roles.extend(neutral)  # add neutrals

classic_roles = [Sheriff, Investigator, Doctor, Jailor, Medium,
                 Escort, Lookout, 'tk', 'rt', Godfather, Mafioso, Framer, SerialKiller,
                 Jester, Executioner
                 ]

game_players = [Mayor, Godfather]  # this a 3 person setup I thought of

# custom setups = https://town-of-salem.fandom.com/wiki/Custom_Setups_(Classic)
# see Don't die on me
# see no u
# see should I attack - is a small gamemode (4/5 players)
# see killing free for all

events = []
