# Python PyQt5 Chat Server

This project implements a chat server using Python and PyQt5. It features a GUI for server-side message monitoring and management, utilizing sockets for network communication and threading for concurrent handling of client connections.

## Features

- **Real-time Chat**: Immediate message exchange between connected clients, displayed in a dual-panel GUI.
- **Multi-client Support**: Handles multiple client connections simultaneously using non-blocking sockets.
- **GUI Notifications**: Visual and audio notifications on the server for events like user connections/disconnections.
- **System Tray Integration**: Minimize the server interface to the system tray for less intrusive operation.

## Prerequisites

Before you run the server, ensure you have the following installed:
- Python 3.x
- PyQt5
- PyQt5-tools (for some additional resources)

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/your-username/PyQt5-Chat-Server.git
cd PyQt5-Chat-Server
