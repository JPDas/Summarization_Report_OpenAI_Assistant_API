import os
import requests
from loguru import logger
from pypdf import PdfReader

from dotenv import load_dotenv

load_dotenv()

reports_generators_tool ={
      "type": "function",
      "function": {
        "name": "get_reports",
        "description": "Get the reports from the CI interface",
        "parameters": {
          "type": "object",
          "properties": {
            "report_name": {
              "type": "string",
              "description": "Report name or file name"
            },
          },
          "required": ["report_name"]
        }
      }
    }


def get_reports(report_name):

    output = ""

    logger.info(f"get reports:: {report_name}")

    # creating a pdf reader object
    reader = PdfReader('Dispute-Resolution-Principals-and-Model-Litigant-Guidelines.pdf')

    # printing number of pages in pdf file
    print(len(reader.pages))

    for page in reader.pages:
        
        # extracting text from page
        output += page.extract_text()

    return output