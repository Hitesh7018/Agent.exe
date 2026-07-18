import os
from dotenv import load_dotenv

import requests

from langchain_groq import ChatGroq
from langchain.messages import SystemMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool

load_dotenv() # loads the .env file

@tool
def job_search_tool(keyword:str,min_salary:int):
    """ This is job search tool, which fetches the job links for user based on their profile.

    Arguments:
    keywords -> The rola the user is looking for(e.g "software","data","network")
    min_salery -> The minimum salary the user is looking for (e.g 100000)
    """

    app_id = os.getenv("ADZUNA_APP_ID")
    app_key= os.getenv("ADZUNA_APP_KEY")
    
    url= "https://api.adzuna.com/v1/api"

    params={
        "app_id":str(app_id),
        "app_key":str(app_key),
        "results_per_page":5,
        "what":keyword,
        "salary_min":min_salary,
        "max_day_old":30,
        
    }
    try:
        response = requests.get(url, params=params, headers={"Accept": "application/json"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Failed to fetch job data: {str(e)}"

class JobSearchAgent:
    def __init__(self):
        llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0.1,
            max_tokens=1024,
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.tools_list = [job_search_tool]
        self.tools_by_names = {t.name: t for t in self.tools_list} # Tool Name -> Tool's Function Object

        self.llm_with_tools = llm.bind_tools(self.tools_list)

    def agent_node(self, state: dict) -> dict:
        messages = state["messages"][-1]

        llm_input = [SystemMessage(content=f"""
        You are an expert job search agent whose task is to analyze the user career evaluation report and find the best
        fit jobs for the user.

        You have access to `job_search_tool`. Use the tool to find relevant opportunities online. The tool will fetch job titles,
        descriptions and URLs.

        The tool takes 2 arguments, which are:

        keyword -> The role the user is looking for (e.g. "Software", "Data", "Network")
        min_salary -> The minimum salary the user is looking for (e.g. 100000)

        Based on the career report, decide the keyword and minimum salary.
        """)]

        llm_input.extend([HumanMessage(content="""Please search jobs for me based on my career report""")])
        llm_input.extend([messages])

        response = self.llm_with_tools.invoke(llm_input)
        print("\n\n\n", response)
        return {"messages": [response]}
        

    def tool_node(self, state: dict) -> dict:
        messages = state["messages"]
        last_message = messages[-1]

        tool_outputs = []

        if hasattr(last_message, "tool_calls"):
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                # tool_id = tool_call["id"]

                tool_function = self.tools_by_names.get(tool_name)

                if tool_function:
                    tool_result = tool_function.invoke(tool_args)
                else:
                    tool_result = f"Error: Tool `{tool_name}` not found"

                tool_outputs.append(
                    ToolMessage(content=f"{tool_name}_OUTPUTS: {str(tool_result)}",
                                tool_name=tool_name)
                )
        
        print("\n\n\n", tool_outputs)
        return {"messages": tool_outputs}

if __name__ == "__main__":
    import traceback
    try:
        print("Invoking job_search_tool with arguments {'keyword': 'Software', 'min_salary': 100000}...")
        response = job_search_tool.invoke({"keyword": "Software", "min_salary": 100000})
        print("Result:")
        print(response)
    except Exception as e:
        print(f"Error invoking tool: {e}")
        traceback.print_exc()