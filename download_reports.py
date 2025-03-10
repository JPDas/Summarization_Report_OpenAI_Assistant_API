import sys
import os
import json
import time
from openai import OpenAI

from dotenv import load_dotenv
from loguru import logger

from utility import reports_generators_tool, get_reports

logger.remove() #remove the old handler. Else, the old one will work along with the new one you've added below'
logger.add(sys.stderr, level="INFO") 


load_dotenv()


class Retriever:

    def __init__(self, assistant_id, thread_id):

        self.assistant_id = assistant_id
        self.thread_id = thread_id
        self.openai = OpenAI()

        if not self.assistant_id:

            assistant = self.openai.beta.assistants.create(
                            name="Report Generator Assistant",
                            instructions="""
                
                                You are an AI summary Assistant. Go step by step because the result of the first step serves as input to the next steps.

                                1. Retrieve the reports from using function calls.  
                                2. Take extreme care to write a summary of the reports downloaded, also answering any questions asked by the user.

                                Please maintain the context and key points from each document while keeping the summaries concise yet detailed. Take your time and provide a direct summary by pulling out the most important key points, facts and opinions.  Use 2000 words or less.""",
            
                            model="gpt-4o-mini",
                            tools=[reports_generators_tool],
                            temperature=0.0,
                            top_p=0.5
                        )
            
            logger.info(f"Assistant created::{assistant}")
            self.assistant_id = assistant.id

        if not self.thread_id:

            thread = self.openai.beta.threads.create()
        
            logger.info(f"Thread is created {thread}")

            self.thread_id = thread.id


    def run_thread(self, query):

        # ==== Create a Message ====
        message = self.openai.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=query
        )

        # === Run our Assistant ===
        run = self.openai.beta.threads.runs.create_and_poll(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions="Please address the user as JP",
        )

        if run.status == "requires_action":
            
            required_actions = run.required_action.submit_tool_outputs.model_dump()
            logger.info(f"Require Actions:: {required_actions}")
            
            for action in required_actions["tool_calls"]:
                tools_outputs = []
                func_name = action["function"]["name"]
                print(func_name)

                arguments = action["function"]["arguments"]
                arguments = json.loads(arguments)
                print(arguments["report_name"])

                if func_name == "get_reports":
                    final_string = get_reports(arguments["report_name"])

                    tools_outputs.append({"tool_call_id": action["id"], "output": final_string})


                    run = self.openai.beta.threads.runs.submit_tool_outputs(thread_id=self.thread_id, run_id=run.id, tool_outputs=tools_outputs)

                    while run.status == "queued" or run.status == "in_progress":
                        run = self.openai.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run.id)

                        time.sleep(1)

                    break
        
        logger.info(f"Run status is {run.status}")
        if run.status == "completed":
            messages = list(self.openai.beta.threads.messages.list(thread_id=self.thread_id, run_id=run.id))

            logger.info(f"Messages::{messages}")
            final_response = messages

        # ==== Steps --- Logs ==
        run_steps = self.openai.beta.threads.runs.steps.list(thread_id=self.thread_id, run_id=run.id)
        logger.info(f"Steps---> {run_steps.data[0]}")

        return final_response