# Slack QA (Question answering) bot

This is a fork of https://github.com/seratch/ChatGPT-in-Slack with additional langchain and integration with https://github.com/go-skynet/LocalAI to run completely locally, without need of any OpenAI account.

The bot allows to ask queries and uses langchain to build a vector database from a website documentation, or a list of Github projects.

![Kairos-TPM-Slackbot](https://github.com/spectrocloud-labs/Slack-QA-bot/assets/2420543/6047e1ff-22d5-4b03-9d73-fcb7fb19a2c1)

## How It Works

You have to start a new thread by mentioning the bot: @<bot name> What's ...?

![Kairos-TPM-Slackbot](https://github.com/spectrocloud-labs/Slack-QA-bot/assets/2420543/6047e1ff-22d5-4b03-9d73-fcb7fb19a2c1)

Note: It _does not_ reply to mentions. That was done in purpose to avoid to send big context back to the LLM, which makes it slow when running entirely on CPU.

## Running the App on Your Local Machine

To run this app on your local machine, you only need to follow these simple steps:

* Create a new Slack app using the manifest-dev.yml file
* Install the app into your Slack workspace
* Retrieve your OpenAI API key at https://platform.openai.com/account/api-keys
* Start the app

```bash
# Create an app-level token with connections:write scope
export SLACK_APP_TOKEN=xapp-1-...
# Install the app into your workspace to grab this token
export SLACK_BOT_TOKEN=xoxb-...
# Visit https://platform.openai.com/account/api-keys for this token
export OPENAI_API_KEY=sk-...

# Optional: gpt-3.5-turbo and gpt-4 are currently supported (default: gpt-3.5-turbo)
export OPENAI_MODEL=gpt-4
# Optional: You can adjust the timeout seconds for OpenAI calls (default: 30)
export OPENAI_TIMEOUT_SECONDS=60


export MEMORY_DIR=/tmp/memory_dir

export OPENAI_API_BASE=http://localhost:8080/v1

export EMBEDDINGS_MODEL_NAME=all-MiniLM-L6-v2

## Repository and sitemap to index in the vector database on start
export SITEMAP="https://kairos.io/sitemap.xml"
export REPOSITORIES="foo,bar"
export foo_CLONE_URL="http://github.com.."
export bar_CLONE_URL="..."
export foo_BRANCH="master"
export GITHUB_PERSONAL_ACCESS_TOKEN=""
export ISSUE_REPOSITORIES="go-skynet/LocalAI,foo/bar,..."

# Optional: When the string is "true", this app translates ChatGPT prompts into a user's preferred language (default: true)
export USE_SLACK_LANGUAGE=true
# Optional: Adjust the app's logging level (default: DEBUG)
export SLACK_APP_LOG_LEVEL=INFO
# Optional: When the string is "true", translate between OpenAI markdown and Slack mrkdwn format (default: false)
export TRANSLATE_MARKDOWN=true

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Running the App for Company Workspaces

Confidentiality of information is top priority for businesses.

This app is open-sourced! so please feel free to fork it and deploy the app onto the infrastructure that you manage.
After going through the above local development process, you can deploy the app using `Dockerfile`, which is placed at the root directory of this project.

The `Dockerfile` is designed to establish a WebSocket connection with Slack via Socket Mode.
This means that there's no need to provide a public URL for communication with Slack.

## Contributions

You're always welcome to contribute! :raised_hands:
When you make changes to the code in this project, please keep these points in mind:
- When making changes to the app, please avoid anything that could cause breaking behavior. If such changes are absolutely necessary due to critical reasons, like security issues, please start a discussion in GitHub Issues before making significant alterations.
- When you have the chance, please write some unit tests. Especially when you touch `internals.py` and add/edit the code that do not call any web APIs, writing tests should be relatively easy.
- Before committing your changes, be sure to run `./validate.sh`. The script runs black (code formatter), flake8 and pytype (static code analyzers).

## The License

The MIT License
