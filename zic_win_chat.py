# zic_chat.py
from argparse import Namespace
import json
import time
import tkinter as tk

from groq import Groq
from FenetrePrincipale import FenetrePrincipale
import Constants as cst
from outils import lire_haute_voix
from secret import GROQ_API_KEY

def make_api_call(client, messages, max_tokens, is_final_answer=False):
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            if attempt == 2:
                if is_final_answer:
                    return {"title": "Error", "content": f"Failed to generate final answer after 3 attempts. Error: {str(e)}"}
                else:
                    return {"title": "Error", "content": f"Failed to generate step after 3 attempts. Error: {str(e)}", "next_action": "final_answer"}
            time.sleep(1)  # Wait for 1 second before retrying

def generate_response(client, prompt):
    messages = [
        {"role": "system", "content": """You are an expert AI assistant that explains your reasoning step by step. For each step, 
         provide a title that describes what you're doing in that step, along with the content.
          Decide if you need another step or if you're ready to give the final answer.
          Respond in JSON format with 'title', 'content', and 'next_action' (either 'continue' or 'final_answer') keys.
          USE AS MANY REASONING STEPS AS POSSIBLE. AT LEAST 3. BE AWARE OF YOUR LIMITATIONS AS AN LLM AND WHAT YOU CAN AND CANNOT DO. 
         IN YOUR REASONING, INCLUDE EXPLORATION OF ALTERNATIVE ANSWERS. 
         CONSIDER YOU MAY BE WRONG, AND IF YOU ARE WRONG IN YOUR REASONING, WHERE IT WOULD BE. 
         FULLY TEST ALL OTHER POSSIBILITIES. YOU CAN BE WRONG. WHEN YOU SAY YOU ARE RE-EXAMINING, 
         ACTUALLY RE-EXAMINE, AND USE ANOTHER APPROACH TO DO SO. DO NOT JUST SAY YOU ARE RE-EXAMINING. USE AT LEAST 3 METHODS TO DERIVE THE ANSWER. USE BEST PRACTICES.

Example of a valid JSON response:
```json
{
    "title": "Identifying Key Information",
    "content": "To begin solving this problem, we need to carefully examine the given information and identify the crucial elements that will guide our solution process. This involves...",
    "next_action": "continue"
}```
""" },
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "Thank you! I will now think step by step following my instructions, starting at the beginning after decomposing the problem."}
    ]
    
    steps = []
    step_count = 1
    total_thinking_time = 0
    
    while True:
        start_time = time.time()
        step_data = make_api_call(client, messages, 300)
        end_time = time.time()
        thinking_time = end_time - start_time
        total_thinking_time += thinking_time
        
        if step_data:
            # Handle potential errors
            if step_data.get('title') == "Error":
                steps.append((f"Etape {step_count}: {step_data.get('title')}", step_data.get('content'), thinking_time))
                break
            
            step_title = f"Etape {step_count}: {step_data.get('title', 'No Title')}"
            step_content = step_data.get('content', 'No Content')
            steps.append((step_title, step_content, thinking_time))
            
            messages.append({"role": "assistant", "content": json.dumps(step_data)})
            
            if step_data.get('next_action') == 'final_answer':
                break
            
            step_count += 1

        else:
            break

    # Generate final answer
    messages.append({"role": "user", "content": "Please provide the final answer based on your reasoning above."})
    
    start_time = time.time()
    final_data = make_api_call(client, messages, 2000, is_final_answer=True)
    end_time = time.time()
    thinking_time = end_time - start_time
    total_thinking_time += thinking_time
    
    if final_data:
        if final_data.get('title') == "Error":
            steps.append(("Final Answer", final_data.get('content'), thinking_time))
        else:
            steps.append(("Final Answer", final_data.get('content', 'No Content'), thinking_time))
        
    return steps, total_thinking_time

def traitement_rapide(texte: str, model_to_use, talking) -> list:
    groq_client = Groq(api_key=GROQ_API_KEY)

    ai_response, _timing = generate_response(
        client=groq_client, prompt=texte
    )
    readable_ai_response = ai_response
    if talking:
        lire_haute_voix(" ".join(readable_ai_response))

    return readable_ai_response


def main(prompt=False):
    """
    ### Entry point of the app ###
    * **If --prompt is True**, the application work in terminal
    and responses will be returned and printed in the terminal
    and exit programme
    """
    model_used = cst.LLAMA370B
    if prompt:
        for line in traitement_rapide(str(prompt), model_to_use=model_used, talking=False):
            zetitl,zecontent,zetime=line
            print(f"\n=> {zetitl}")
            print(f"\n\t{zecontent}")
            print(f"{zetime}\n")
        exit()

    model_used = cst.LLAMA370B.split(":")[0]
    lire_haute_voix("Ia sélectionnée :" + model_used)
    print(
        "ZicChatbotAudio\n"
        + cst.STARS * cst.WIDTH_TERM
        + "\nChargement... Veuillez patienter\n"
        + cst.STARS * cst.WIDTH_TERM
    )

    root = tk.Tk(className="YourAssistant")
    root.title = "AssIstant - "  # type: ignore

    fenetrePrincipale = FenetrePrincipale(
        master=root, title="AssIstant", model_to_use=model_used
    )

    fenetrePrincipale.title = "MyApp"
    fenetrePrincipale.mainloop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a ArcHydro schema")
    parser.add_argument(
        "--prompt", metavar="prompt", required=False, help="the prompt to ask"
    )
    args: Namespace = parser.parse_args()

    # Début du programme
    main(prompt=args.prompt)
