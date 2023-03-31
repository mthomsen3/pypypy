"""
messages.py: Defines various message classes for different message types 
used in client-server communication, including HelloMessage, VersionMessage, 
RegisterMessage, LoginMessage, LoginResponseMessage, StatusMessage, 
AuthorizationMessage, QuitMessage, ChatMessage, UserListUpdateMessage, 
RequestUserListMessage, and RequestMessageHistoryMessage.
"""
# Define message classes for different message types

import shared.lobby as Lobby

class HelloMessage:
    def __init__(self, message):
        self.type = "HELLO"
        self.message = message

class VersionMessage:
    def __init__(self, version):
        self.type = "VERSION"
        self.version = version

class RegisterMessage:
    def __init__(self, username, email, password):
        self.type = "REGISTER"
        self.username = username
        self.email = email
        self.password = password

class LoginMessage:
    def __init__(self, email, password):
        self.type = "LOGIN"
        self.email = email
        self.password = password

class LoginResponseMessage:
    def __init__(self, status, username):
        self.type = "LOGIN_RESPONSE"
        self.status = status
        self.username = username

class StatusMessage:
    def __init__(self, status):
        self.type = "STATUS"
        self.status = status

class AuthorizationMessage:
    def __init__(self, token):
        self.type = "AUTHORIZATION"
        self.token = token

class DisconnectMessage:
    def __init__(self, username):
        self.type = 'DISCONNECT'
        self.username = username

class ChatMessage:
    def __init__(self, username, message):
        self.type = "CHAT_MESSAGE"
        self.username = username
        self.message = message

class UserListUpdateMessage:
    def __init__(self, users):
        self.type = 'USER_LIST_UPDATE'
        self.users = users
    
class RequestUserListMessage:
    def __init__(self, usernames=None):
        self.type = 'REQUEST_USER_LIST'
        self.usernames = usernames if usernames else []

class RequestMessageHistoryMessage:
    def __init__(self, messages=None):
        self.type = "REQUEST_MESSAGE_HISTORY"
        self.messages = messages if messages else []

# Can be sent by client or server
# Sent as request (empty) and response to request
class RequestLobbyListMessage:
    def __init__(self, lobbies=None):
        self.type = "REQUEST_LOBBY_LIST"
        self.lobbies = lobbies if lobbies else []
        
class LobbyListUpdateMessage:
    def __init__(self, lobbies=None):
        self.type = "LOBBY_LIST_UPDATE"
        self.lobbies = lobbies if lobbies else []






class CreateLobbyMenuRequestMessage:
    def __init__(self, owner):
        self.type = "CREATE_LOBBY_MENU_REQUEST"
        self.owner = owner

class CreateLobbyMenuRequestAcceptedMessage:
    def __init__(self, owner):
        self.type = "CREATE_LOBBY_MENU_REQUEST_ACCEPTED"
        self.owner = owner

# lobby_id is created by the server
# CreateLobbyMessage is sent by the client to create a lobby
class CreateLobbyRequestMessage:
    def __init__(self, owner, lobby_name, game_type, max_players, lobby_password=None):
        self.type = "CREATE_LOBBY"
        self.owner = owner
        self.lobby_name = lobby_name
        self.game_type = game_type
        self.max_players = max_players
        self.lobby_password = lobby_password

class LobbyFailedMessage:
    def __init__(self, error_message):
        self.type = "LOBBY_FAILED"
        self.error_message = error_message

# LobbyCreatedMessage is sent by the server to the client
class LobbyCreatedMessage:
    def __init__(self, lobby_id, owner, players, groups, lobby_name, game_type, max_players, lobby_password=None):
        self.type = "LOBBY_CREATED"
        self.lobby_id = lobby_id
        self.players = players
        self.groups = groups
        self.owner = owner
        self.lobby_name = lobby_name
        self.game_type = game_type
        self.max_players = max_players
        self.lobby_password = lobby_password

class JoinLobbyMessage:
    def __init__(self, lobby_id, username, lobby_password=None):
        self.type = "JOIN_LOBBY"
        self.lobby_id = lobby_id
        self.username = username
        self.lobby_password = lobby_password

class JoinLobbyResponseMessage:
    def __init__(self, lobby_id, status, username, players):
        self.type = "JOIN_LOBBY_RESPONSE"
        self.lobby_id = lobby_id
        self.status = status
        self.username = username
        self.players = players

class LobbyNotFoundMessage:
    def __init__(self, error_message):
        self.type = "LOBBY_NOT_FOUND"
        self.error_message = error_message


class LeaveLobbyMessage:
    def __init__(self, lobby_id, username):
        self.type = "LEAVE_LOBBY"
        self.lobby_id = lobby_id
        self.username = username

class LobbyUpdateMessage:
    def __init__(self, lobby_id, players, groups, owner, lobby_name, game_type, max_players, lobby_password=None):
        self.type = "LOBBY_UPDATE"
        self.lobby_id = lobby_id
        self.players = players
        self.groups = groups
        self.owner = owner
        self.lobby_name = lobby_name
        self.game_type = game_type
        self.max_players = max_players
        self.lobby_password = lobby_password

class LobbyClosedMessage:
    def __init__(self, owner, lobby_id):
        self.type = "LOBBY_CLOSED"
        self.owner = owner
        self.lobby_id = lobby_id






class StartGameMessage:
    def __init__(self, lobby_id):
        self.type = "START_GAME"
        self.lobby_id = lobby_id

class GameStartedMessage:
    def __init__(self, session_id):
        self.type = "GAME_STARTED"
        self.session_id = session_id

class PlayerActionMessage:
    def __init__(self, session_id, action):
        self.type = "PLAYER_ACTION"
        self.session_id = session_id
        self.action = action

class GameStateUpdateMessage:
    def __init__(self, session_id, game_state):
        self.type = "GAME_STATE_UPDATE"
        self.session_id = session_id
        self.game_state = game_state




