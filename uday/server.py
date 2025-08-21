import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from livekit import api as lk_api
from livekit.api import LiveKitAPI, ListRoomsRequest

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Get list of existing rooms
async def get_rooms():
    client = LiveKitAPI()
    rooms = await client.room.list_rooms(ListRoomsRequest())
    await client.aclose()
    return [room.name for room in rooms.rooms]

# Generate a unique room name
async def generate_room_name():
    name = "room-" + str(uuid.uuid4())[:8]
    rooms = await get_rooms()
    while name in rooms:
        name = "room-" + str(uuid.uuid4())[:8]
    return name

@app.route("/getToken")
def get_token():
    name = request.args.get("name", "guest")
    room = request.args.get("room")

    if not room:
        # Because Flask route is sync, we must call async function properly
        import asyncio
        room = asyncio.run(generate_room_name())

    token = lk_api.AccessToken(
        os.getenv("LIVEKIT_API_KEY"),
        os.getenv("LIVEKIT_API_SECRET"),
    ).with_identity(name).with_grants(
        lk_api.VideoGrants(
            room_join=True,
            room=room,
        )
    )

    return jsonify({"token": token.to_jwt(), "room": room})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
