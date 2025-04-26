import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain.globals import set_verbose, set_debug
from langchain_core.tools import tool
import datetime
import sys


agent = create_react_agent( "openai:gpt-4o-mini")

