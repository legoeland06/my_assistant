# zic_chat.py
from argparse import Namespace
import json
import time
import tkinter as tk

from groq import Groq
from FenetrePrincipale import FenetrePrincipale
import Constants as cst
from StoppableThread import StoppableThread
from outils import create_asyncio_task, lire_haute_voix
from secret import GROQ_API_KEY


async def make_api_call(client, messages, max_tokens, is_final_answer=False):
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            if attempt == 2:
                if is_final_answer:
                    return {
                        "title": "Error",
                        "content": f"Failed to generate final answer after 3 attempts. Error: {str(e)}",
                    }
                else:
                    return {
                        "title": "Error",
                        "content": f"Failed to generate step after 3 attempts. Error: {str(e)}",
                        "next_action": "final_answer",
                    }
            time.sleep(1)  # Wait for 1 second before retrying


async def generate_response(client, prompt, min_steps: str, max_steps: str):
    messages = [
        {
            "role": "system",
            "content": f"""You are an expert AI assistant that explains your reasoning step by step. For each step, 
         provide a title that describes what you're doing in that step, along with the content.
          Decide if you need another step or if you're ready to give the final answer.
          Respond in JSON format with 'title', 'content', and 'next_action' (either 'continue' or 'final_answer') keys.
          USE AS MANY REASONING STEPS AS POSSIBLE. AT LEAST """
            + min_steps
            + """ AND AT MOST """
            + max_steps
            + """. BE AWARE OF YOUR LIMITATIONS AS AN LLM AND WHAT YOU CAN AND CANNOT DO. 
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
""",
        },
        {"role": "user", "content": prompt},
        {
            "role": "assistant",
            "content": "Thank you! I will now think step by step following my instructions, starting at the beginning after decomposing the problem.",
        },
    ]

    steps = []
    step_count = 1
    total_thinking_time = 0

    while True:
        start_time = time.time()
        step_data = await make_api_call(client, messages, 300)
        end_time = time.time()
        thinking_time = end_time - start_time
        total_thinking_time += thinking_time

        if step_data:
            # Handle potential errors
            if step_data.get("title") == "Error":
                steps.append(
                    (
                        f"Etape {step_count}: {step_data.get('title')}",
                        step_data.get("content"),
                        thinking_time,
                    )
                )
                break

            step_title = f"Etape {step_count}: {step_data.get('title', 'No Title')}"
            step_content = step_data.get("content", "No Content")
            steps.append((step_title, step_content, thinking_time))

            messages.append({"role": "assistant", "content": json.dumps(step_data)})

            if step_data.get("next_action") == "final_answer":
                break

            step_count += 1

        else:
            break

    # Generate final answer
    messages.append(
        {
            "role": "user",
            "content": "Please provide the final answer based on your reasoning above.",
        }
    )

    start_time = time.time()
    final_data = await make_api_call(client, messages, 2000, is_final_answer=True)
    end_time = time.time()
    thinking_time = end_time - start_time
    total_thinking_time += thinking_time

    if final_data:
        if final_data.get("title") == "Error":
            steps.append(("Final Answer", final_data.get("content"), thinking_time))
        else:
            steps.append(
                ("Final Answer", final_data.get("content", "No Content"), thinking_time)
            )

    return steps, total_thinking_time


async def traitement_rapide(
    texte: str, min_steps: str, max_steps: str, talking: bool
) -> list:
    groq_client = Groq(api_key=GROQ_API_KEY)

    ai_response, _timing = await generate_response(
        client=groq_client, prompt=texte, min_steps=min_steps, max_steps=max_steps
    )
    readable_ai_response = ai_response
    if talking:
        lire_haute_voix(" ".join(readable_ai_response))

    return readable_ai_response


async def term_response(prompt: str, min_steps: str, max_steps: str, talk: bool):
    total_response = await traitement_rapide(
        str(prompt),
        min_steps=min_steps,
        max_steps=max_steps,
        talking=False,
    )
    for line in total_response:
        zetitl, zecontent, zetime = line
        print(f"\n## {zetitl}")
        print(f"\n\t{zecontent}")
        print(f"{zetime}\n")

    if talk and total_response.__len__():
        lire_haute_voix(str(total_response))


def main(prompt=False, min_steps: str = "3", max_steps: str = "3", talk=False):
    """
    ### Entry point of the app ###
    * **If --prompt is True**, the application work in terminal
    and responses will be returned and printed in the terminal
    and exit programme
    """
    if prompt:
        _thread = StoppableThread(
            None,
            lambda: create_asyncio_task(
                async_function=term_response(
                    str(prompt),
                    min_steps=min_steps,
                    max_steps=max_steps,
                    talk=talk,
                )
            ),
        )
        _thread.name = "mode_terminal"
        _thread.start()
        _thread.join()
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
    parser.add_argument(
        "--min_steps", metavar="min_steps", required=False, help="the min_steps to ask"
    )
    parser.add_argument(
        "--max_steps", metavar="max_steps", required=False, help="the max_steps to ask"
    )
    parser.add_argument("--talk", metavar="talk", required=False, help="the talker")
    args: Namespace = parser.parse_args()

    # Début du programme
    main(
        prompt=args.prompt,
        min_steps=args.min_steps,
        max_steps=args.max_steps,
        talk=args.talk,
    )
