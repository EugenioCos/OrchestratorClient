## Create a job:

- job/jobX.json

## Setup the job

```
{
    "root": "/Users/ab/Documents/python/IA",
    "prompts": [
        ...
        {
            "title": "Correzione2",
            "text": "Ripristina come prima delle modifiche",
            "agent": "Correttore",
            "context_prompts": ["Correzione", "Valutazione Correzione"],
            "think": false,
            "commit": true,
            "reset_on_fail": ["Correzione2"],
            "reset_on_success": ["Correzione", "Valutazione Correzione", "Correzione2"],
            "next_on_fail": "Correzione2",
            "next_on_success": "Correzione"
        },
        ...
    ]
}
```

- text: str, Text of the prompt.
- context_prompts: list[str], list of prompts to be used as context.
- think: bool, if true thinking is added to the context.
- tools: bool, true to permit tool use.
- commit: bool,
    - null -> do not attempt to commit.
    - true -> changes and commit expected.
    - false -> no changes expected.
- next_on_fail: list[str],  title of the next prompt in case of fail.
- next_on_success: str, title of the next prompt in case of success.
- reset_on_fail: list[str] reset this prompts in case of fail.
- reset_on_success: list[str], reset this prompts in case of success.
- permit_end: bool, if true model can end the work. In case ai decides to not end, 'next_on_fail' is applied.

## Setup settings.json:

```
{
    "source": "https://github.com/my/repo.git",
    "job_name": "name of the job file with no .json extension",
    "existing_branch": null to create from source | "the name of the folder in the worspace to work in",
    "model": "pulled model in ollama",
    "response_path": "relative path in the target for all ia response log data",
    "workspace_path": "absolute path for ai's workspace directory",
    "ignore_elements": [
        "list of files and directories names to ignore",
        "IA_INFO",
        "workspace",
        "requirements.txt",
        ".git",
        "Modelfile",
        ".gitignore"
    ]
}
```

# Setup python

- Create virtual environment:

> python3 -m venv venv

- Source the virtual environment:

> source venv/bin/activate

- Install requirements:

> python3 -m pip install -r requirements.txt

# Execute

> python3 src/main.py
