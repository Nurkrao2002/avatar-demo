import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='agent_debug.log',
    filemode='w'
)
logging.info("Agent script started")

try:
    from dotenv import load_dotenv
    logging.info("Imported dotenv")
    from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
    logging.info("Imported prompts")
    from livekit import agents
    logging.info("Imported livekit.agents")
    from livekit.agents import AgentSession, Agent, RoomInputOptions
    logging.info("Imported livekit.agents components")
    from livekit.plugins import (
        google,
        noise_cancellation,
        tavus,
    )
    logging.info("Imported livekit.plugins")
    import os
    logging.info("Imported os")
    from tools import get_weather, search_web, send_email, open_url
    logging.info("Imported tools")

    load_dotenv()
    logging.info("dotenv loaded")

except Exception as e:
    logging.error(f"An error occurred during import: {e}", exc_info=True)
    # The script will exit here if an exception is raised, which is what we want
    # for debugging.
    raise


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            tools=[
                get_weather,
                search_web,
                send_email,
                open_url,
            ],
        )


async def entrypoint(ctx: agents.JobContext):
    logging.info("Starting agent entrypoint")
    try:
        session = AgentSession(
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede"
            )
        )
        logging.info("AgentSession created")

        avatar = tavus.AvatarSession(
          replica_id=os.environ.get("REPLICA_ID"),
          persona_id=os.environ.get("PERSONA_ID"),
          api_key=os.environ.get("TAVUS_API_KEY"),
        )
        logging.info("AvatarSession created")

        # Start the avatar and wait for it to join
        await avatar.start(session, room=ctx.room)
        logging.info("Avatar started")

        await session.start(
            room=ctx.room,
            agent=Assistant(),
            room_input_options=RoomInputOptions(
                # LiveKit Cloud enhanced noise cancellation
                # - If self-hosting, omit this parameter
                # - For telephony applications, use `BVCTelephony` for best results
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )
        logging.info("Session started")

        await ctx.connect()
        logging.info("Context connected")

        await session.generate_reply(
            instructions=SESSION_INSTRUCTION,
        )
        logging.info("Reply generated")

    except Exception as e:
        logging.error(f"An error occurred in entrypoint: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    except Exception as e:
        logging.error(f"An error occurred running the app: {e}", exc_info=True)
        raise
