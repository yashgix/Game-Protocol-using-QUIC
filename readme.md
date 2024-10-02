# CS544-Game-Protocol-using-Quic

This project implements a game protocol using QUIC (Quick UDP Internet Connections) in Python. It enables reliable game state synchronization, basic player authentication, a chat system, disconnection and reconnection handling, and error handling.

## Contributors

- Yash Gupta -yg444@drexel.edu
- Shubham Jadhav - sj3237@drexel.edu

## Features Implemented

### Reliable Game State Synchronization
The protocol ensures that game state synchronization between the client and server is reliable.

### Basic Player Authentication
Players can create accounts with unique usernames and passwords, which are stored securely. Additionally, players can log in using their credentials.

### Chat System
A chat system allows players to communicate with each other in real-time during gameplay.

### Disconnection and Reconnection Handling
The protocol handles disconnections gracefully and allows players to reconnect to the server without losing their progress.

### Error Handling and Reliability
Errors are handled robustly, ensuring the stability and reliability of the protocol.

## Protocol Requirements

### Stateful Implementation
Both the client and server implement and validate the statefulness of the protocol using a Deterministic Finite Automaton (DFA).

### Service Binding
The server binds to a hardcoded port number, and the client defaults to that port number.

### Client Configuration
The client can specify the hostname or IP address of the server via command line arguments or a configuration file.

### Server Configuration
Server configuration information, such as the port number, can be provided via command line parameters or a configuration file.

### User Interface
The user interface of the client is command-line-based, ensuring ease of use without requiring users to know the underlying protocol commands.

## Files

- echo_client.py: Client-side implementation of the game protocol.
- echo_server.py: Server-side implementation of the game protocol.
- pdu.py: Contains the Protocol Data Unit (PDU) definitions for message types.
- echo_quic.py: Implements the QUIC connection and stream handling.
- echo.py: Main script to run the client or server based on user input.
- quic_engine.py: Provides functions for building QUIC configurations and running the client or server.

### Running the Server

To start the server, use the following command:

- python echo.py server

### Running the Client

To start the client, use the following command:

- python echo.py client


## Dependencies

- aioquic: Library for QUIC (Quick UDP Internet Connections) support.
- asyncio: Library for asynchronous programming in Python.

# How to Use

1. Run the server and client using the commands provided above and make sure all the dependancies and neccessary files are installed and exists in place.

2. Once the client starts, you are provided with 2 options:
- 1. Create Account
- 2. Login
You can either create a account or login to authenticate the user.

3. Make sure to start 2 client in 2 different terminals.

4. Once 2 clients (players) have been authenticated, a chatbox will open up and the players can communicate with each other using the chat system feature.

P.S ONCE YOU LOGIN IT TAKES SOME TIME TO ENTER THE CHAT SYSTEM SO PLEASE WAIT BEFORE IT WORKS.
