import openai


def prompt_inject(prompt, apikey):
    openai.api_key = apikey
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    print(res["choices"][0]["message"]["content"])
