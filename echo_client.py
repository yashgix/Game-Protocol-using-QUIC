
import asyncio
import json
from typing import Dict
from echo_quic import EchoQuicConnection, QuicStreamEvent
import pdu

async def echo_client_proto(scope: Dict, conn: EchoQuicConnection):
    print('[cli] starting client')
    
    while True:
        print("1. Create account")
        print("2. Login")
        choice = input("Enter your choice (1 or 2): ")
        
        if choice == "1":
            username = input("Enter a username: ")
            password = input("Enter a password: ")
            
            # Send create account message
            create_account_dgram = pdu.Datagram(pdu.MSG_TYPE_CREATE_ACCOUNT, json.dumps({"username": username, "password": password}))
            create_account_qs = QuicStreamEvent(conn.new_stream(), create_account_dgram.to_bytes(), False)
            await conn.send(create_account_qs)
            
            # Receive create account response
            message: QuicStreamEvent = await conn.receive()
            dgram_resp = pdu.Datagram.from_bytes(message.data)
            print(dgram_resp.msg)
            
        elif choice == "2":
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            
            new_stream_id = conn.new_stream()
            
            # Send join message with username and password
            join_dgram = pdu.Datagram(pdu.MSG_TYPE_JOIN, json.dumps({"username": username, "password": password}))
            join_qs = QuicStreamEvent(new_stream_id, join_dgram.to_bytes(), False)
            await conn.send(join_qs)
            
            # Receive join response
            message: QuicStreamEvent = await conn.receive()
            dgram_resp = pdu.Datagram.from_bytes(message.data)
            print(dgram_resp.msg)
            
            if dgram_resp.mtype != pdu.MSG_TYPE_ERROR:
                break  # Successful login, proceed to conversation
        else:
            print("Invalid choice. Please try again.")
    
    while True:
        message = input("Enter a message (or 'quit' to exit): ")
        
        if message.lower() == 'quit':
            # Send leave message
            leave_dgram = pdu.Datagram(pdu.MSG_TYPE_LEAVE, "Client left")
            leave_qs = QuicStreamEvent(new_stream_id, leave_dgram.to_bytes(), False)
            await conn.send(leave_qs)
            break
        
        # Send chat message
        chat_dgram = pdu.Datagram(pdu.MSG_TYPE_CHAT, message)
        chat_qs = QuicStreamEvent(new_stream_id, chat_dgram.to_bytes(), False)
        await conn.send(chat_qs)
        
        # Receive and display incoming messages
        while True:
            try:
                message: QuicStreamEvent = await asyncio.wait_for(conn.receive(), timeout=1.0)
                dgram_resp = pdu.Datagram.from_bytes(message.data)
                print(dgram_resp.msg)
            except asyncio.TimeoutError:
                break