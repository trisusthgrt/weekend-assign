import requests
import json

DNA_TOKEN= ""
# using wrapper api which internally call chat gpt api
OPENAI_API_WRAPPER = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"

OPENAI_API_HEADERS = {
'x-api-token': DNA_TOKEN,
'Content-Type': 'application/json',
'Cookie': 'csrftoken=Ia7mAreRCxbvmPwNUbiRdOqdf74jrT2X'
}

def get_request_payload(systemprompt, userprompt): 
    payload = json.dumps({
    "messages": [
    {
    "role": "system",
    "content": systemprompt,
    },
    {
    "role": "user",
    "content": userprompt,
    }
    ],
    "max_tokens": "2000",
    "model": "gpt-4",
    "temperature": "0",
    "top_p": "1",
    })
    return payload

def generate_openai_response(systemprompt, userprompt):
   payload = get_request_payload(systemprompt, userprompt)
   response = requests.request("POST", OPENAI_API_WRAPPER, headers=OPENAI_API_HEADERS, data=payload)
   parsedJson = json.loads(response.content)
   print(json.dumps(parsedJson, indent=4))

##########  SYSTEM PROMPT  ###############################################################################################################################################

systemprompt = """
You are a secretary, your job is to generate a Minutes of meeting for a given transcript, delimited by ####, that'd be circulated to the wider audience.
Minutes of meeting should include
- Date and time of the meeting
- Names of the meeting participants and those unable to attend, if any.
- Key points discussed in the meeting, for example: Actions taken or agreed to be taken,  Voting outcomes (if necessary, details regarding who made motions; who seconded and approved or via show of hands, etc.), Motions taken or rejected, Items to be held over or New business etc.
- Next steps
- Overall tone of the meeting
- Next meeting date and time (optional, if its a regular recurrence)
"""

##########  USER PROMPT  ################################################################################################################################################

userprompt = """
Here is a transcript for a daily standup of an engineering team.

####
Alice: Good morning everyone, I trust you are all well?

James: Hello Alice, yes, I'm doing good, thank you. 

Emma: Good morning, Alice. I'm doing well too. 

Mike: Hello Alice, yes, I'm doing alright.

Sophie: Morning Alice, all well here.

Alice: Great to hear. Let's get started then! James, can we kick off with your update?

James: Sure, Alice. I've been working on the backend code for our new feature. However, I'm facing a bit of an issue, there seems to be a bug that I can't identify.

Alice: I see, I think our tech lead, Mike, might be able to help you here. 

Mike: Yes, James. I'll need to understand the bug a bit better. Could you share your screen and walk me through it?

James: Sure, Mike. *Shares screen and walks through the issue*

Mike: Thanks, James. I see what's happening. Here's what you can do: Try running the debugger to isolate the issue, then check the database queries for any inconsistencies. I'll send you a checklist of what to look for.

James: Thank you, Mike. I'll do that and keep you posted.

Alice: That sounds like a plan. Emma, how about you?

Emma: Alice, I've been working on the frontend, but I'm having some problems with integrating the API's. 

Alice: Mike, can you also take a look at this?

Mike: Sure, Alice. Emma, could you share your screen?

Emma: Sure. *Shares screen and explains the problem*

Mike: Alright, Emma. It seems like there's an issue with the API endpoints. I'll send you a step-by-step guide on how to properly integrate these API's. Also, let's have a session tomorrow to ensure everything's working fine.

Emma: That sounds perfect, Mike. I'll look forward to that.

Alice: Excellent! Sophie, your update?

Sophie: I'm all good, Alice. No issues on my end.

Alice: Wonderful! Let's continue to keep the momentum going. Thank you, everyone.

Everyone: Thanks, Alice. Goodbye.

Alice: Goodbye, everyone.
####
"""

generate_openai_response(systemprompt, userprompt)