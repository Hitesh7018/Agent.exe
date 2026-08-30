print("I AM RUNNING CAREER_AGENT.PY")
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from App.service.rag_service import RAGService

load_dotenv()


@tool
def get_resume_data(query: str):
    """This is RAG tool which get information of user's career,
    including skills, experiences, projects, education and intrest from their resume data.
    
    Arguments:
    query -> The section or question about resume that will fetch a perticular data about candidate.
    """
    print("rag tool started")
    rag_service = RAGService()
    print("rag service initialized")
    retriever = rag_service.get_retriever()
    print("retriever initialized")

    response = retriever.invoke(query)
    print("response received")

    return response


class CareerAssessmentAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=1000,
            api_key=os.getenv("GROQ_API_KEY"),
            max_retries=1,      # don't silently retry for a long time
            timeout=30,
        )

        self.tools = [get_resume_data]
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def agent_node(self, state: dict) -> dict:
        messages = state["messages"]
        system_prompt = SystemMessage(content=(
            "You are an autonomous career assessment agent. Your instructions are strict:\n"
            "1. Use the `get_resume_data` tool to fetch all the information about the user.\n"
            "2. DO NOT ask human or the user for any clarifications, missing details or missing sections\n"
            "3. If certain details are missing in the retrieved data, proceed using ONLY what is available.\n"
            "4. You MUST compile and output a final `CANDIDATE CAREER EVALUATION REPORT` based on the retrieved data.\n"
            "5. Get resume data tool argument; query -> The section or a question about the resume that will fetch a particular data about the candidate."
            "6. DO NOT GIVE GENERIC QUERY TO THE TOOL. The tool can fetch data FROM the resume. Be very specific on what data you require from the resume."
            "7. Example queries for the tool call: Query = 'What are the work experiences of the user?', 'What is the educational background of the user?', 'What are the skills of the user?', 'What are the projects of the user?', 'What are the interests of the user?'"
            "Ensure the phrase `CANDIDATE CAREER EVALUATION REPORT` is clearly printed at the start of your final report."
        ))

        full_messages = [system_prompt] + messages
        responce = self.llm_with_tools.invoke(full_messages)
        return {"messages": [responce]}

    def tool_node(self, state: dict) -> dict:
        messages = state["messages"]
        last_message = messages[-1]
        tool_output = []

        if hasattr(last_message, "tool_calls"):
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                print("\n\n\n", tool_name, tool_args, tool_id)

                tool_function = self.tools_by_name.get(tool_name)

                if tool_function:
                    tool_result = tool_function.invoke(tool_args)
                else:
                    tool_result = f"Error: Tool '{tool_name}' not found."

                tool_output.append(
                    ToolMessage(content=(str(tool_result)),
                                tool_call_id=tool_id,
                                name=tool_name)
                )

        return {"messages": tool_output}


if __name__ == "__main__":
    print("========== MAIN STARTED  ==========")

    docs = get_resume_data.invoke(
        "What are the work experiences of the user?"
    )

    print("========== DATA RECEIVED ==========")
    print(docs)

    print("========== PROGRAM FINISHED ==========")
               
   