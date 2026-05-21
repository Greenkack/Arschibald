import inspect

import fastapi

app = fastapi.FastAPI()


def auto_api(module):
    for name, func in inspect.getmembers(module, inspect.isfunction):
        app.get(f"/{name}")(func)
# auto_api(your_module)
# uvicorn.run(app)
