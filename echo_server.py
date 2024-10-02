
import os
import asyncio
import json
from typing import Coroutine, Dict
from echo_quic import EchoQuicConnection, QuicStreamEvent
import pdu

clients = {}  # Dictionary to store connected clients and their stream IDs
disconnected_clients = {}  # Dictionary to store disconnected clients and their last known state

def load_players_data():
    if not os.path.exists("players.json"):
        with open("players.json", "w") as file:
            json.dump({"players": []}, file, indent=2)
    
    with open("players.json", "r") as file:
        return json.load(file)

def save_players_data(data):
    with open("players.json", "w") as file:
        json.dump(data, file, indent=2)

def authenticate_player(username, password):
    data = load_players_data()
    for player in data["players"]:
        if player["username"] == username and player["password"] == password:
            return True
    return False

def create_player_account(username, password):
    data = load_players_data()
    for player in data["players"]:
        if player["username"] == username:
            return False  # Username already exists
    
    new_player = {"username": username, "password": password}
    data["players"].append(new_player)
    save_players_data(data)
    
    return True

async def echo_server_proto(scope: Dict, conn: EchoQuicConnection):
    stream_id = conn.new_stream()
    buffer = b""

    while True:
        try:
            message: QuicStreamEvent = await conn.receive()
            buffer += message.data

            while True:
                try:
                    decoded_data, end_pos = json.JSONDecoder().raw_decode(buffer.decode('utf-8'))
                    dgram_in = pdu.Datagram(**decoded_data)
                    print("[svr] received message: ", dgram_in.msg)

                    if dgram_in.mtype == pdu.MSG_TYPE_CREATE_ACCOUNT:
                        player_info = json.loads(dgram_in.msg)
                        username = player_info["username"]
                        password = player_info["password"]
                        if create_player_account(username, password):
                            success_msg = "Account created successfully. You can now login."
                            success_dgram = pdu.Datagram(pdu.MSG_TYPE_CHAT, success_msg)
                            success_qs = QuicStreamEvent(stream_id, success_dgram.to_bytes(), False)
                            await conn.send(success_qs)
                        else:
                            error_msg = "Username already exists. Please choose a different username."
                            error_dgram = pdu.Datagram(pdu.MSG_TYPE_ERROR, error_msg)
                            error_qs = QuicStreamEvent(stream_id, error_dgram.to_bytes(), False)
                            await conn.send(error_qs)
                    elif dgram_in.mtype == pdu.MSG_TYPE_JOIN:
                        player_info = json.loads(dgram_in.msg)
                        username = player_info["username"]
                        password = player_info["password"]
                        if authenticate_player(username, password):
                            clients[stream_id] = {"username": username, "conn": conn}
                            join_msg = f"{username} joined the chat"
                            await broadcast_message(stream_id, join_msg)
                        else:
                            error_msg = "Authentication failed. Invalid username or password."
                            error_dgram = pdu.Datagram(pdu.MSG_TYPE_ERROR, error_msg)
                            error_qs = QuicStreamEvent(stream_id, error_dgram.to_bytes(), False)
                            await conn.send(error_qs)
                    elif dgram_in.mtype == pdu.MSG_TYPE_CHAT:
                        username = clients[stream_id]["username"]
                        chat_msg = f"{username}: {dgram_in.msg}"
                        await broadcast_message(stream_id, chat_msg)
                    elif dgram_in.mtype == pdu.MSG_TYPE_LEAVE:
                        username = clients[stream_id]["username"]
                        disconnected_clients[stream_id] = {"username": username, "last_message": dgram_in.msg}
                        del clients[stream_id]
                        leave_msg = f"{username} left the chat"
                        await broadcast_message(stream_id, leave_msg)
                        break

                    buffer = buffer[end_pos:].lstrip()
                    if not buffer:
                        break
                except (json.JSONDecodeError, UnicodeDecodeError, KeyError) as e:
                    print(f"Error processing message: {e}")
                    error_msg = f"Server error: {str(e)}"
                    error_dgram = pdu.Datagram(pdu.MSG_TYPE_ERROR, error_msg)
                    error_qs = QuicStreamEvent(stream_id, error_dgram.to_bytes(), False)
                    await conn.send(error_qs)
                    break

        except Exception as e:
            print(f"Error in server protocol: {e}")
            # Handle the exception, log the error, or take appropriate action
            # You can choose to close the connection or send an error message to the client
            error_msg = f"Server error: {str(e)}"
            error_dgram = pdu.Datagram(pdu.MSG_TYPE_ERROR, error_msg)
            error_qs = QuicStreamEvent(stream_id, error_dgram.to_bytes(), False)
            await conn.send(error_qs)
            break

async def broadcast_message(sender_stream_id, message):
    for stream_id, client_info in clients.items():
        if stream_id != sender_stream_id:
            dgram_out = pdu.Datagram(pdu.MSG_TYPE_CHAT, message)
            rsp_msg = dgram_out.to_bytes()
            rsp_evnt = QuicStreamEvent(stream_id, rsp_msg, False)
            await client_info["conn"].send(rsp_evnt)