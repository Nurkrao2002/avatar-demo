from dotenv import load_dotenv
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    noise_cancellation,
)
from mcp_client import MCPServerSse
from mcp_client.agent_tools import MCPToolsIntegration
import os
from tools import open_url
from livekit.plugins import tavus
load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_INSTRUCTION,
                         tools=[open_url],)


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="shimmer"
        )
    )


    avatar = tavus.AvatarSession(
      replica_id=os.environ.get("REPLICA_ID"),  
      persona_id=os.environ.get("PERSONA_ID"),  
      api_key=os.environ.get("TAVUS_API_KEY"),
    )

    # Start the avatar and wait for it to join
    await avatar.start(session, room=ctx.room)


    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions=SESSION_INSTRUCTION,
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))