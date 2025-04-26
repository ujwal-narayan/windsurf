import asyncio
import os
import sys
import datetime

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain.globals import set_verbose, set_debug
from langchain_core.tools import tool


sys.path.append("whatsapp_mcp_server")
from whatsapp_mcp_server.main import (
    search_contacts,
    list_messages,
    list_chats,
    get_chat,
    get_contact_chats,
    get_last_interaction,
    get_message_context,
    send_message,
    send_file,
    send_audio_message,
    download_media
)

# set_verbose(True)
# set_debug(True)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_API_KEY")
@tool
def get_current_time() -> datetime.datetime:
    """
    Returns the current time.

    Returns
    -------
    datetime.datetime
        The current time.
    """
    return datetime.datetime.now()

@tool
def get_crm(user_id: str) -> str:
    """
    Fetches the CRM data for the user with the given user_id.
    """
    print(f"Fetching CRM data for {user_id}")
    try:
        with open(f"crm/{user_id}.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No CRM data found for the user"
    
@tool
def write_crm(user_id: str, crm_data: str):
    """
    Writes the CRM data for the user with the given user_id.
    """
    print(f"Writing CRM data for {user_id}")
    with open(f"crm/{user_id}.txt", "w") as f:
        f.write(crm_data)
    return "CRM data written successfully"

@tool
def get_future_time(
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    days: int = 0,
    weeks: int = 0,
) -> datetime.datetime:
    """
    Gives the time in seconds since the epoch of the time after the specified amount of time.
    """
    return datetime.datetime.now() + datetime.timedelta(
        seconds=seconds,
        minutes=minutes,
        hours=hours,
        days=days,
        weeks=weeks,
    )

@tool
def get_last_time(
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    days: int = 0,
    weeks: int = 0,
) -> datetime.datetime:
    """
    Gives the time in seconds since the epoch of the time before the specified amount of time.

    Parameters
    ----------
    seconds : int, optional
        The number of seconds, by default 0.
    minutes : int, optional
        The number of minutes, by default 0.
    hours : int, optional
        The number of hours, by default 0.
    days : int, optional
        The number of days, by default 0.
    weeks : int, optional
        The number of weeks, by default 0.

    Returns
    -------
    datetime.datetime
        The time before the specified amount of time.
    """
    return datetime.datetime.now() - datetime.timedelta(
        seconds=seconds,
        minutes=minutes,
        hours=hours,
        days=days,
        weeks=weeks,
    )

async def get_user_input(prompt: str) -> str:
    """Get user input asynchronously"""
    print(prompt, end='', flush=True)
    return await asyncio.get_event_loop().run_in_executor(None, input)

async def process_with_crm_agent(messages, tools):
    """Process messages with the CRM agent"""
    crm_system_prompt = """
    You are a **proactive, detail-oriented assistant** tasked with building and maintaining a Personal CRM from WhatsApp conversations.

    ## ✨ CRM Responsibilities

    - Analyze **only the contact's messages** (ignore the user's own messages).
    - Extract as much personal information as possible based on what the contact **has explicitly stated or reasonably implied**.
    - Output a **structured, easy-to-read JSON object** for the CRM.

    ### 📚 CRM Content to Extract

    Extract and organize the following **(based only on the contact's own messages)**:

    1. **Basic Personal Information**
       - Full Name (and nicknames)
       - Phone Number(s)
       - Email Address(es)
       - Home and Work Address
       - Birthday, Age
       - Relationship to the user (Family, Friend, Colleague, Acquaintance, etc.)

    2. **Professional and Academic Background**
       - Current Company and Job Title
       - Past Employers
       - Universities/Schools attended
       - Degrees and Certifications

    3. **Personal Interests and Lifestyle**
       - Hobbies and Interests
       - Likes and Dislikes
       - Favorite foods, drinks, movies, books, destinations
       - Pets and animal preferences

    4. **Social and Family Connections**
       - Names of family members, friends, colleagues
       - Their relationship to the contact

    5. **Important Life Events**
       - Birthdays, Anniversaries, Career milestones
       - Future plans (moving cities, new jobs, vacations)

    6. **Personality Insights**
       - Personality traits
       - Communication style (e.g., casual, formal, humorous)

    7. **Miscellaneous Useful Insights**
       - Habits, routines, clubs, associations
       - Aspirations and goals

    ### 📦 CRM Output Format

    Output the CRM in this **JSON format**:

    ```json
    {
      "person": {
        "full_name": "",
        "nicknames": [],
        "phone_numbers": [],
        "emails": [],
        "addresses": [],
        "birthday": "",
        "relationship": "",
        "work": {
          "company": "",
          "job_title": "",
          "work_address": ""
        },
        "education": {
          "university": "",
          "degree": ""
        },
        "interests": [],
        "dislikes": [],
        "favorite_things": {
          "foods": [],
          "movies": []
        },
        "social_connections": [
          {
            "name": "",
            "relationship": ""
          }
        ],
        "important_events": [],
        "personality_traits": [],
        "miscellaneous": []
      }
    }
    ```

    ## ⚡ Important Rules

    - **Only trigger actions** based on information from the **contact's own messages**.
    - **Be comprehensive**: Prefer capturing more information rather than less.
    - **Respect structure**: Always output well-formed JSON when dealing with CRM data.
    - **Be proactive**: Detect and act on CRM updates without explicit user prompting.
   
    Always check if a CRM exists for the user. If it does, use the existing CRM. If it does not, generate a new CRM.
    If a CRM does not exist, you must generate a new CRM. You can do this by fetching all the messages from the contact. Set the limit to be -1 and the include_context to be False in the list_messages function.
    If a new CRM is generated, you must update the CRM file. 
    If a CRM already exists, then you dont need to fetch all the messages again. Instead, you can use the existing CRM file, and the new messages to update the CRM. 
    
    Check if a CRM exists or Fetch the CRM by using the get_crm tool.
    Write the CRM to the file by using the write_crm tool.
    
    Always write CRM to the file.
    """
    
    crm_agent = create_react_agent(
        "openai:gpt-4.1-mini",
        tools
    )
    
    crm_messages = [{"role": "system", "content": crm_system_prompt}]
    crm_messages.extend(messages)
    
    value = await crm_agent.ainvoke(
        {"messages": crm_messages}
    )
    return value["messages"][-1].content

async def process_with_event_agent(messages, tools):
    """Process messages with the event scheduling agent"""
    event_system_prompt = """
    You are a **proactive, detail-oriented assistant** tasked with detecting and managing events from incoming WhatsApp messages.

    ## 🕒 Event Management Responsibilities

    When analyzing messages, look for:

    ### 🎉 Event Detection

    - If an **event** is mentioned (e.g., meeting, party, travel plan):
      - Use available tools such as `get_current_time` to set appropriate event time if needed.
      - Use google maps to set the location of the event. If the location is not found, set the location according to the discussed location i.e as Text.
      - Create a **calendar event** using the available calendar tool.
      - If you are sure, don't ask for confirmation. Go ahead and create the event. You can inform the user once you have created the event.
      - Only if you are not sure, ask for confirmation.
      - All timings are in IST unless otherwise specified. So ensure the event time is set in IST.
      - Consider messages from both me and the contact when creating the event.
      - Do not set the email etc unless the email is explicitly mentioned or the email is found in the CRM.
      

    ## ⚡ Important Rules

    - **Be proactive**: Detect and act on events without explicit user prompting.
    - **Be precise**: Ensure event details are accurate and complete.
    - **Be considerate**: Only create events when you're confident about the details.
    - If no event is found, just return "No event found".
    """
    
    event_agent = create_react_agent(
        "openai:gpt-4.1-mini",
        tools
    )
    
    event_messages = [{"role": "system", "content": event_system_prompt}]
    event_messages.extend(messages)
    
    value = await event_agent.ainvoke(
        {"messages": event_messages}
    )
    return value["messages"][-1].content


def get_chats_in_the_last_n_minutes(n: int) -> dict:
    chats = list_chats(limit=1000)
    now = datetime.datetime.now(datetime.timezone.utc)
    chats = [chat for chat in chats if chat.last_message_time > now - datetime.timedelta(minutes=n)]
    user_chats = {}
    for chat in chats:
        chat_messages = list_messages(limit=-1, chat_jid=chat.jid, include_context=False)
        if chat_messages:
            chat_id = chat.jid
            user_name = chat.name
            user_chats[chat_id] = {"name": user_name, "messages": chat_messages}
    return user_chats


    
async def main():
    async with MultiServerMCPClient(
        {
            "whatsapp": {
                "command": "/Users/badwolf/.local/bin/uv",
                "args": [
                    "--directory",
                    "/Users/badwolf/work/hackathon/windsurf25/whatsapp-mcp/whatsapp_mcp_server",
                    "run",
                    "main.py"
                ],
                "transport": "stdio",
            },
              "google-calendar": {
                "command": "node",
                "args": ["/Users/badwolf/work/hackathon/windsurf25/whatsapp-mcp/google-calendar-mcp/build/index.js"],
                "transport": "stdio",
            },
            "google-maps": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-google-maps"],
                "env": {
                    "GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY
                }
            }
        }
    ) as client:
        tools = client.get_tools()
        tools.extend([get_current_time, get_last_time, get_future_time, get_crm, write_crm])
        messages = [] 
        async def process_chats():
            nonlocal messages
            while True:
                print("\nChecking for new chats in the last 10 minutes...")
                new_chats = get_chats_in_the_last_n_minutes(10)
                if new_chats:
                    print(f"Found {len(new_chats)} new chats to process")
                    for chat in new_chats:
                        print(f"\nProcessing chat: {chat}")
                        messages = [{"role": "user", "content": f"New messages in chat :: {new_chats[chat]["name"]} :: {new_chats[chat]["messages"]}"}]
                        
                        # Run both agents in parallel
                        crm_result, event_result = await asyncio.gather(
                            process_with_crm_agent(messages, tools),
                            process_with_event_agent(messages, tools)
                        )
                        messages.append({"role": "assistant", "content": crm_result})
                        messages.append({"role": "assistant", "content": event_result})
                        
                        # Print results
                        print("\nCRM Update Result:")
                        print(crm_result)
                        print("\nEvent Scheduling Result:")
                        print(event_result)
                        
                        # Save results to file
                        with open("output.txt", "a") as f:
                            f.write(f"\nProcessing chat: {new_chats[chat]['name']}\n")
                            f.write("CRM Update Result:\n")
                            f.write(str(crm_result) + "\n\n")
                            f.write("Event Scheduling Result:\n")
                            f.write(str(event_result) + "\n")
                
                await asyncio.sleep(600)  # Sleep for 10 minutes
        
        async def handle_user_input():
            nonlocal messages
            while True:
                user_input = await get_user_input("User: ")
                if user_input:
                    messages.append({"role": "user", "content": user_input})
                    
                    # Run both agents in parallel
                    crm_result, event_result = await asyncio.gather(
                        process_with_crm_agent(messages, tools),
                        process_with_event_agent(messages, tools)
                    )
                    
                    # Print results
                    print("\nCRM Update Result:")
                    print(crm_result)
                    print("\nEvent Scheduling Result:")
                    print(event_result)
                    
                    # Save results to file
                    with open("output.txt", "a") as f:
                        f.write("\nUser Input Processing:\n")
                        f.write("CRM Update Result:\n")
                        f.write(str(crm_result) + "\n\n")
                        f.write("Event Scheduling Result:\n")
                        f.write(str(event_result) + "\n")
        
        # Run both tasks concurrently
        await asyncio.gather(
            # process_chats(),
            handle_user_input()
        )

if __name__ == "__main__":
    asyncio.run(main())

