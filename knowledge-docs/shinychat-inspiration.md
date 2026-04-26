---
title: "Get inspired"
site: "Shiny for Python"
source: "https://shiny.posit.co/py/docs/genai-inspiration.html"
language: "en"
description: "Build interactive web applications easily with the power of Python’s data and scientific stack."
word_count: 1337
---

Before jumping into tools and techniques for building Generative AI apps, it’s helpful to see some inspiring examples of what’s possible. In this article, we’ll highlight a few apps that leverage Gen AI in useful ways, from streaming chatbots to more bespoke interfaces. Make sure to also check out the [templates](https://shiny.posit.co/py/templates/) for more examples of Shiny + AI.

ImportantResponsible use

Generative AI is a powerful tool. When used responsibly, it offers some incredible opportunities for enhancing user experiences and productivity. However, when Gen AI outcomes lack reliability, transparency, and reproducibility, it can lead to worse, not better, outcomes. This is especially true when data analysis is involved and accuracy is paramount. Thankfully, LLMs have some useful techniques for increasing verifiability in outcomes, such as [tool calling](https://shiny.posit.co/py/docs/genai-tools.html) where you can effectively equip the LLM with the reproducible tools to accomplish certain tasks, and allow the user to verify the methodology and results.

In this article, we’ll highlight some of these techniques, and how they can be used to build more reliable and reproducible applications.

## Chatbots

In [chatbots](https://shiny.posit.co/py/docs/genai-chatbots.html), we’ll cover the ins and outs of building a chatbot with `Chat()`. Chatbots are the most familiar interface to Generative AI, and can be used for a wide variety of tasks, from coding assistants to enhancing interactive dashboards.

### Coding assistant 👩💻

LLMs excel when they are instructed to focus on particular task(s), and provided the context necessary to complete them accurately. This is especially true for coding assistants, such as the [Shiny Assistant](https://shiny.posit.co/blog/posts/shiny-assistant/) which leverages an LLM to help you build Shiny apps faster. Just describe the app you want to build, and Shiny Assistant does its best to give you a complete working example that runs in your browser.

<video controls title="Building a mortgage calculator with Shiny Assistant"><source src="https://shiny.posit.co/blog/posts/shiny-assistant/mortgage-calculator-1.mp4"></video>

Although a “standard” chat interface like ChatGPT can help you write Shiny code, there are two main things that make Shiny Assistant a better experience:

1. **Context**: Shiny Assistant is [provided instructions](https://github.com/posit-dev/shiny-assistant/blob/main/shinyapp/app_prompt_python.md) and up-to-date knowledge about Shiny, which allows it to generate more accurate code and better looking results.
2. **Playground**: Shiny Assistant takes the generated code and runs the app in your browser via [shinylive](https://shinylive.io/py/examples/), allowing you to iterate on the app and see the results in real-time.

Although the playground aspect of Shiny Assistant is an impressive technical feat, it’s not strictly necessary to make your own useful coding/learning assistant with context important to your domain. In fact, we’ve found that creating a simple chatbot that is simply instructed to focus on helping you learn about a new package, and providing the documentation for that package, to be surprisingly effective. One such example includes the [chatlas assistant](https://github.com/cpsievert/chatlas-assistant), which helps users learn about the `chatlas` package (our recommended way of programming with LLMs) by providing documentation and examples.

### Enhanced dashboards 📊

LLMs are also very good at extracting [structured data](https://shiny.posit.co/py/docs/genai-structured-data.html) from unstructured text, which is useful for a wide variety of tasks. One interesting application is translating a user’s natural language query into a SQL query. Combining this ability with [tools](https://shiny.posit.co/py/docs/genai-tools.html) to actually run the SQL query on the data and [reactively](https://shiny.posit.co/py/docs/reactive-foundations.html) update relevant views makes for a powerful way to “drill down” into your data. Moreover, by making the SQL query accessible to the user, you can enhance the verifiability and reproducibility of the LLM’s response.

#### Query chat

The [`querychat` package](https://github.com/posit-dev/querychat) provides tools to help you more easily leverage this idea in your own Shiny apps. A straightforward use of querychat is shown below, where the user can ask a natural language question about the `titanic` dataset, and the LLM generates a SQL query that can be run on the data:

![Screenshot of the “querychat” app, which leverages LLMs to generate SQL queries that match a user’s natural language query.](https://shiny.posit.co/py/images/genai-querychat.png)

Screenshot of the “querychat” app, which leverages LLMs to generate SQL queries that match a user’s natural language query.

The app above is available as a [template](https://shiny.posit.co/py/templates/querychat/index.html):

```bash
shiny create --template querychat \
    --github posit-dev/py-shiny-templates/gen-ai
```

#### Sidebot

A more advanced application of this concept is to drive multiple views of the data with a single natural language query. An implementation of this idea is available in the [sidebot](https://github.com/jcheng5/py-sidebot) repo. It defaults to the `tips` dataset, but without much effort, you can adapt it to another dataset of your choosing.

![Screenshot of the “sidebot” app, which leverages LLMs to translate natural language to SQL, and tools to reactively update the dashboard.](https://shiny.posit.co/py/images/genai-sidebot.png)

Screenshot of the “sidebot” app, which leverages LLMs to translate natural language to SQL, and tools to reactively update the dashboard.

The app above is available as a [template](https://shiny.posit.co/py/templates/sidebot/index.html):

```bash
shiny create --template querychat \
    --github posit-dev/py-shiny-templates/gen-ai
```

Sidebot also demonstrates how one can leverage an LLM’s ability to “see” images and generate natural language descriptions of them. Specifically, by clicking on the ✨ icon, the user is provided with a natural language description of the visualization, which can be useful for accessibility or for users who are not as familiar with the data.

![Screenshot of the “sidebot” app with a tooltip describing the visualization.](https://shiny.posit.co/py/images/genai-sidebot-tooltip.png)

Screenshot of the “sidebot” app with a tooltip describing the visualization.

### Guided exploration 🧭

Chatbots are also a great way to guide users through an experience, such as a story, game, or learning activity. The `Chat()` component’s [input suggestion](https://shiny.posit.co/py/docs/genai-chatbots.html#suggest-input) feature provides a particularly useful interface for this, as it makes it very easy for users to ‘choose their own adventure’ with little to no typing.

For example, this “Choose your own Data Science Adventure” app starts by collecting some basic user information, then generates relevant hypothetical data science scenarios. Based on the scenario the user chooses, the app then guides the user through a series of questions, ultimately leading to a data science project idea and deliverable:

![Screenshot of the “Choose your own Data Science Adventure” app.](https://shiny.posit.co/py/images/genai-data-science-adventure.png)

Screenshot of the “Choose your own Data Science Adventure” app.

The app above is available as a [template](https://shiny.posit.co/py/templates/data-sci-adventure/index.html):

```bash
shiny create --template data-sci-adventure \
    --github posit-dev/py-shiny-templates/gen-ai
```

Another example is the “What’s for Dinner?” app, which helps the user brainstorm dinner (or other) recipe ideas based on available ingredients and other input. In addition to brainstorming through recipe ideas, it also leverages [structured data extraction](https://shiny.posit.co/py/docs/genai-structured-data.html) to put the recipe in a structured format that could be ingested by a database.

## Streaming markdown

`MarkdownStream()` [usage](#basic-usage) is fairly straightforward, but the potential applications may not be immediately obvious. In a generative AI setting, a common pattern is to gather [input](https://shiny.posit.co/py/components/#inputs) from the user, then pass that info along to a prompt template for the LLM to generate a response. Here are a couple motivating examples:

### Workout plan generator 💪

The app illustrated below uses an LLM to generate a workout plan based on a user’s fitness goals, experience level, and available equipment:

![Screenshot of the app with a generated workout plan.](https://shiny.posit.co/py/images/genai-workout-plan.png)

Screenshot of the app with a generated workout plan.

When the user clicks ‘Get Workout’, the app fills a prompt template that looks roughly like this, and passes the result as input to the LLM:

```python
prompt = f"""
Generate a brief {input.duration()}-minute workout plan for a {input.goal()} fitness goal.
On a scale of 1-10, I have a level  {input.experience()} experience,
works out {input.daysPerWeek()} days per week, and have access to:
{", ".join(input.equipment()) if input.equipment() else "no equipment"}.
"""
```

From this prompt, the LLM responds with a workout plan, which is streamed into the app via `MarkdownStream()` component. Go ahead and visit the [live app](https://github.com/posit-dev/py-shiny-templates/tree/main/gen-ai/workout-plan) to see it in action, or grab the source code to run it locally:

The app above is available as a [template](https://shiny.posit.co/py/templates/workout-plan/index.html):

```bash
shiny create --template workout-plan \
    --github posit-dev/py-shiny-templates/gen-ai
```

### Image describer 🖼️

The app below uses an LLM to generate a description of an image based on a user-provided URL:

![Screenshot of an app that generates an image description.](https://shiny.posit.co/py/images/genai-image-describer.png)

Screenshot of an app that generates an image description.

When the user clicks ‘Describe Image’, the app passes the image URL to the LLM, which generates an overall description, tag keywords, as well as estimates on location, photographer, etc. This content is then streamed into the `MarkdownStream()` component (inside of a card) as it’s being produced.

This slightly more advanced example also demonstrates how to route the same response stream to multiple output views: namely, both the `MarkdownStream()` and a `Chat()` component. This allows the user to make follow-up requests or ask questions about the image description.

![Screenshot of the image description app with the offcanvas chat made visible.](https://shiny.posit.co/py/images/genai-image-describer-chat.png)

Screenshot of the image description app with the offcanvas chat made visible.

The app above is available as a [template](https://shiny.posit.co/py/templates/):

```bash
shiny create --github jonkeane/shinyImages
```