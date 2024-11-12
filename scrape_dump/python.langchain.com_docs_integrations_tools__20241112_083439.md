# Content from https://python.langchain.com/docs/integrations/tools/

[Skip to main content](#__docusaurus_skipToContent_fallback)

On this page

[Tools](/docs/concepts/tools/) are utilities designed to be called by a model: their inputs are designed to be generated by models, and their outputs are designed to be passed back to models.

A [toolkit](/docs/concepts/tools/#toolkits) is a collection of tools meant to be used together.

info

If you'd like to write your own tool, see [this how-to](/docs/how_to/custom_tools/).
If you'd like to contribute an integration, see [Contributing integrations](/docs/contributing/how_to/integrations/).

The following table shows tools that execute online searches in some shape or form:

| Tool/Toolkit | Free/Paid | Return Data |
| --- | --- | --- |
| [Bing Search](/docs/integrations/tools/bing_search/) | Paid | URL, Snippet, Title |
| [Brave Search](/docs/integrations/tools/brave_search/) | Free | URL, Snippet, Title |
| [DuckDuckgoSearch](/docs/integrations/tools/ddg/) | Free | URL, Snippet, Title |
| [Exa Search](/docs/integrations/tools/exa_search/) | 1000 free searches/month | URL, Author, Title, Published Date |
| [Google Search](/docs/integrations/tools/google_search/) | Paid | URL, Snippet, Title |
| [Google Serper](/docs/integrations/tools/google_serper/) | Free | URL, Snippet, Title, Search Rank, Site Links |
| [Jina Search](/docs/integrations/tools/jina_search/) | 1M Response Tokens Free | URL, Snippet, Title, Page Content |
| [Mojeek Search](/docs/integrations/tools/mojeek_search/) | Paid | URL, Snippet, Title |
| [SearchApi](/docs/integrations/tools/searchapi/) | 100 Free Searches on Sign Up | URL, Snippet, Title, Search Rank, Site Links, Authors |
| [SearxNG Search](/docs/integrations/tools/searx_search/) | Free | URL, Snippet, Title, Category |
| [SerpAPI](/docs/integrations/tools/serpapi/) | 100 Free Searches/Month | Answer |
| [Tavily Search](/docs/integrations/tools/tavily_search/) | 1000 free searches/month | URL, Content, Title, Images, Answer |
| [You.com Search](/docs/integrations/tools/you/) | Free for 60 days | URL, Title, Page Content |

## Code Interpreter [​](\#code-interpreter "Direct link to Code Interpreter")

The following table shows tools that can be used as code interpreters:

| Tool/Toolkit | Supported Languages | Sandbox Lifetime | Supports File Uploads | Return Types | Supports Self-Hosting |
| --- | --- | --- | --- | --- | --- |
| [Azure Container Apps dynamic sessions](/docs/integrations/tools/azure_dynamic_sessions/) | Python | 1 Hour | ✅ | Text, Images | ❌ |
| [Bearly Code Interpreter](/docs/integrations/tools/bearly/) | Python | Resets on Execution | ✅ | Text | ❌ |
| [E2B Data Analysis](/docs/integrations/tools/e2b_data_analysis/) | Python. In beta: JavaScript, R, Java | 24 Hours | ✅ | Text, Images, Videos | ✅ |
| [Riza Code Interpreter](/docs/integrations/tools/riza/) | Python, JavaScript, PHP, Ruby | Resets on Execution | ✅ | Text | ✅ |

## Productivity [​](\#productivity "Direct link to Productivity")

The following table shows tools that can be used to automate tasks in productivity tools:

| Tool/Toolkit | Pricing |
| --- | --- |
| [Github Toolkit](/docs/integrations/tools/github/) | Free |
| [Gitlab Toolkit](/docs/integrations/tools/gitlab/) | Free for personal project |
| [Gmail Toolkit](/docs/integrations/tools/gmail/) | Free, with limit of 250 quota units per user per second |
| [Infobip Tool](/docs/integrations/tools/infobip/) | Free trial, with variable pricing after |
| [Jira Toolkit](/docs/integrations/tools/jira/) | Free, with [rate limits](https://developer.atlassian.com/cloud/jira/platform/rate-limiting/) |
| [Office365 Toolkit](/docs/integrations/tools/office365/) | Free with Office365, includes [rate limits](https://learn.microsoft.com/en-us/graph/throttling-limits) |
| [Slack Toolkit](/docs/integrations/tools/slack/) | Free |
| [Twilio Tool](/docs/integrations/tools/twilio/) | Free trial, with [pay-as-you-go pricing](https://www.twilio.com/en-us/pricing) after |

## Web Browsing [​](\#web-browsing "Direct link to Web Browsing")

The following table shows tools that can be used to automate tasks in web browsers:

| Tool/Toolkit | Pricing | Supports Interacting with the Browser |
| --- | --- | --- |
| [MultiOn Toolkit](/docs/integrations/tools/multion/) | 40 free requests/day | ✅ |
| [PlayWright Browser Toolkit](/docs/integrations/tools/playwright/) | Free | ✅ |
| [Requests Toolkit](/docs/integrations/tools/requests/) | Free | ❌ |

## Database [​](\#database "Direct link to Database")

The following table shows tools that can be used to automate tasks in databases:

| Tool/Toolkit | Allowed Operations |
| --- | --- |
| [Cassandra Database Toolkit](/docs/integrations/tools/cassandra_database/) | SELECT and schema introspection |
| [SQLDatabase Toolkit](/docs/integrations/tools/sql_database/) | Any SQL operation |
| [Spark SQL Toolkit](/docs/integrations/tools/spark_sql/) | Any SQL operation |

## All tools [​](\#all-tools "Direct link to All tools")

| Name | Description |
| --- | --- |
| [AINetwork Toolkit](/docs/integrations/tools/ainetwork) | AI Network is a layer 1 blockchain designed to accommodate large-scal... |
| [Alpha Vantage](/docs/integrations/tools/alpha_vantage) | Alpha Vantage Alpha Vantage provides realtime and historical financia... |
| [Amadeus Toolkit](/docs/integrations/tools/amadeus) | This notebook walks you through connecting LangChain to the Amadeus t... |
| [ArXiv](/docs/integrations/tools/arxiv) | This notebook goes over how to use the arxiv tool with an agent. |
| [AskNews](/docs/integrations/tools/asknews) | AskNews infuses any LLM with the latest global news (or historical ne... |
| [AWS Lambda](/docs/integrations/tools/awslambda) | Amazon AWS Lambda is a serverless computing service provided by Amazo... |
| [Azure AI Services Toolkit](/docs/integrations/tools/azure_ai_services) | This toolkit is used to interact with the Azure AI Services API to ac... |
| [Azure Cognitive Services Toolkit](/docs/integrations/tools/azure_cognitive_services) | This toolkit is used to interact with the Azure Cognitive Services AP... |
| [Azure Container Apps dynamic sessions](/docs/integrations/tools/azure_dynamic_sessions) | Azure Container Apps dynamic sessions provides a secure and scalable ... |
| [Shell (bash)](/docs/integrations/tools/bash) | Giving agents access to the shell is powerful (though risky outside a... |
| [Bearly Code Interpreter](/docs/integrations/tools/bearly) | Bearly Code Interpreter allows for remote execution of code. This mak... |
| [Bing Search](/docs/integrations/tools/bing_search) | Bing Search is an Azure service and enables safe, ad-free, location-a... |
| [Brave Search](/docs/integrations/tools/brave_search) | This notebook goes over how to use the Brave Search tool. |
| [Cassandra Database Toolkit](/docs/integrations/tools/cassandra_database) | Apache Cassandra® is a widely used database for storing transactional... |
| [CDP](/docs/integrations/tools/cdp_agentkit) | The CDP Agentkit toolkit contains tools that enable an LLM agent to i... |
| [ChatGPT Plugins](/docs/integrations/tools/chatgpt_plugins) | OpenAI has deprecated plugins. |
| [ClickUp Toolkit](/docs/integrations/tools/clickup) | ClickUp is an all-in-one productivity platform that provides small an... |
| [Cogniswitch Toolkit](/docs/integrations/tools/cogniswitch) | CogniSwitch is used to build production ready applications that can c... |
| [Connery Toolkit and Tools](/docs/integrations/tools/connery) | Using the Connery toolkit and tools, you can integrate Connery Action... |
| [Dall-E Image Generator](/docs/integrations/tools/dalle_image_generator) | OpenAI Dall-E are text-to-image models developed by OpenAI using deep... |
| [Databricks Unity Catalog (UC)](/docs/integrations/tools/databricks) | This notebook shows how to use UC functions as LangChain tools, with ... |
| [DataForSEO](/docs/integrations/tools/dataforseo) | DataForSeo provides comprehensive SEO and digital marketing data solu... |
| [Dataherald](/docs/integrations/tools/dataherald) | This notebook goes over how to use the dataherald component. |
| [DuckDuckGo Search](/docs/integrations/tools/ddg) | This guide shows over how to use the DuckDuckGo search component. |
| [E2B Data Analysis](/docs/integrations/tools/e2b_data_analysis) | E2B's cloud environments are great runtime sandboxes for LLMs. |
| [Eden AI](/docs/integrations/tools/edenai_tools) | This Jupyter Notebook demonstrates how to use Eden AI tools with an A... |
| [Eleven Labs Text2Speech](/docs/integrations/tools/eleven_labs_tts) | This notebook shows how to interact with the ElevenLabs API to achiev... |
| [Exa Search](/docs/integrations/tools/exa_search) | Exa is a search engine fully designed for use by LLMs. Search for doc... |
| [File System](/docs/integrations/tools/filesystem) | LangChain provides tools for interacting with a local file system out... |
| [FinancialDatasets Toolkit](/docs/integrations/tools/financial_datasets) | The financial datasets stock market API provides REST endpoints that ... |
| [Github Toolkit](/docs/integrations/tools/github) | The Github toolkit contains tools that enable an LLM agent to interac... |
| [Gitlab Toolkit](/docs/integrations/tools/gitlab) | The Gitlab toolkit contains tools that enable an LLM agent to interac... |
| [Gmail Toolkit](/docs/integrations/tools/gmail) | This will help you getting started with the GMail toolkit. This toolk... |
| [Golden Query](/docs/integrations/tools/golden_query) | Golden provides a set of natural language APIs for querying and enric... |
| [Google Books](/docs/integrations/tools/google_books) | Overview |
| [Google Cloud Text-to-Speech](/docs/integrations/tools/google_cloud_texttospeech) | Google Cloud Text-to-Speech enables developers to synthesize natural-... |
| [Google Drive](/docs/integrations/tools/google_drive) | This notebook walks through connecting a LangChain to the Google Driv... |
| [Google Finance](/docs/integrations/tools/google_finance) | This notebook goes over how to use the Google Finance Tool to get inf... |
| [Google Imagen](/docs/integrations/tools/google_imagen) | Imagen on Vertex AI brings Google's state of the art image generative... |
| [Google Jobs](/docs/integrations/tools/google_jobs) | This notebook goes over how to use the Google Jobs Tool to fetch curr... |
| [Google Lens](/docs/integrations/tools/google_lens) | This notebook goes over how to use the Google Lens Tool to fetch info... |
| [Google Places](/docs/integrations/tools/google_places) | This notebook goes through how to use Google Places API |
| [Google Scholar](/docs/integrations/tools/google_scholar) | This notebook goes through how to use Google Scholar Tool |
| [Google Search](/docs/integrations/tools/google_search) | This notebook goes over how to use the google search component. |
| [Google Serper](/docs/integrations/tools/google_serper) | This notebook goes over how to use the Google Serper component to sea... |
| [Google Trends](/docs/integrations/tools/google_trends) | This notebook goes over how to use the Google Trends Tool to fetch tr... |
| [Gradio](/docs/integrations/tools/gradio_tools) | There are many 1000s of Gradio apps on Hugging Face Spaces. This libr... |
| [GraphQL](/docs/integrations/tools/graphql) | GraphQL is a query language for APIs and a runtime for executing thos... |
| [HuggingFace Hub Tools](/docs/integrations/tools/huggingface_tools) | Huggingface Tools that supporting text I/O can be |
| [Human as a tool](/docs/integrations/tools/human_tools) | Human are AGI so they can certainly be used as a tool to help out AI ... |
| [IFTTT WebHooks](/docs/integrations/tools/ifttt) | This notebook shows how to use IFTTT Webhooks. |
| [Infobip](/docs/integrations/tools/infobip) | This notebook that shows how to use Infobip API wrapper to send SMS m... |
| [Ionic Shopping Tool](/docs/integrations/tools/ionic_shopping) | Ionic is a plug and play ecommerce marketplace for AI Assistants. By ... |
| [Jina Search](/docs/integrations/tools/jina_search) | This notebook provides a quick overview for getting started with Jina... |
| [Jira Toolkit](/docs/integrations/tools/jira) | This notebook goes over how to use the Jira toolkit. |
| [JSON Toolkit](/docs/integrations/tools/json) | This notebook showcases an agent interacting with large JSON/dict obj... |
| [Lemon Agent](/docs/integrations/tools/lemonai) | Lemon Agent helps you build powerful AI assistants in minutes and aut... |
| [Memorize](/docs/integrations/tools/memorize) | Fine-tuning LLM itself to memorize information using unsupervised lea... |
| [Mojeek Search](/docs/integrations/tools/mojeek_search) | The following notebook will explain how to get results using Mojeek S... |
| [MultiOn Toolkit](/docs/integrations/tools/multion) | MultiON has built an AI Agent that can interact with a broad array of... |
| [NASA Toolkit](/docs/integrations/tools/nasa) | This notebook shows how to use agents to interact with the NASA toolk... |
| [Nuclia Understanding](/docs/integrations/tools/nuclia) | Nuclia automatically indexes your unstructured data from any internal... |
| [NVIDIA Riva: ASR and TTS](/docs/integrations/tools/nvidia_riva) | NVIDIA Riva |
| [Office365 Toolkit](/docs/integrations/tools/office365) | Microsoft 365 is a product family of productivity software, collabora... |
| [OpenAPI Toolkit](/docs/integrations/tools/openapi) | We can construct agents to consume arbitrary APIs, here APIs conforma... |
| [Natural Language API Toolkits](/docs/integrations/tools/openapi_nla) | Natural Language API Toolkits (NLAToolkits) permit LangChain Agents t... |
| [OpenWeatherMap](/docs/integrations/tools/openweathermap) | This notebook goes over how to use the OpenWeatherMap component to fe... |
| [Oracle AI Vector Search: Generate Summary](/docs/integrations/tools/oracleai) | Oracle AI Vector Search is designed for Artificial Intelligence (AI) ... |
| [Pandas Dataframe](/docs/integrations/tools/pandas) | This notebook shows how to use agents to interact with a Pandas DataF... |
| [Passio NutritionAI](/docs/integrations/tools/passio_nutrition_ai) | To best understand how NutritionAI can give your agents super food-nu... |
| [PlayWright Browser Toolkit](/docs/integrations/tools/playwright) | Playwright is an open-source automation tool developed by Microsoft t... |
| [Polygon IO Toolkit and Tools](/docs/integrations/tools/polygon) | This notebook shows how to use agents to interact with the Polygon IO... |
| [PowerBI Toolkit](/docs/integrations/tools/powerbi) | This notebook showcases an agent interacting with a Power BI Dataset.... |
| [PubMed](/docs/integrations/tools/pubmed) | PubMed® comprises more than 35 million citations for biomedical liter... |
| [Python REPL](/docs/integrations/tools/python) | Sometimes, for complex calculations, rather than have an LLM generate... |
| [Reddit Search](/docs/integrations/tools/reddit_search) | In this notebook, we learn how the Reddit search tool works. |
| [Requests Toolkit](/docs/integrations/tools/requests) | We can use the Requests toolkit to construct agents that generate HTT... |
| [Riza Code Interpreter](/docs/integrations/tools/riza) | The Riza Code Interpreter is a WASM-based isolated environment for ru... |
| [Robocorp Toolkit](/docs/integrations/tools/robocorp) | This notebook covers how to get started with Robocorp Action Server a... |
| [SceneXplain](/docs/integrations/tools/sceneXplain) | SceneXplain is an ImageCaptioning service accessible through the Scen... |
| [SearchApi](/docs/integrations/tools/searchapi) | This notebook shows examples of how to use SearchApi to search the we... |
| [SearxNG Search](/docs/integrations/tools/searx_search) | This notebook goes over how to use a self hosted SearxNG search API t... |
| [Semantic Scholar API Tool](/docs/integrations/tools/semanticscholar) | This notebook demos how to use the semantic scholar tool with an agen... |
| [SerpAPI](/docs/integrations/tools/serpapi) | This notebook goes over how to use the SerpAPI component to search th... |
| [Slack Toolkit](/docs/integrations/tools/slack) | This will help you getting started with the Slack toolkit. For detail... |
| [Spark SQL Toolkit](/docs/integrations/tools/spark_sql) | This notebook shows how to use agents to interact with Spark SQL. Sim... |
| [SQLDatabase Toolkit](/docs/integrations/tools/sql_database) | This will help you getting started with the SQL Database toolkit. For... |
| [StackExchange](/docs/integrations/tools/stackexchange) | Stack Exchange is a network of question-and-answer (Q&A) websites on ... |
| [Steam Toolkit](/docs/integrations/tools/steam) | Steam (Wikipedia)) is a video game digital distribution service and s... |
| [Tavily Search](/docs/integrations/tools/tavily_search) | Tavily's Search API is a search engine built specifically for AI agen... |
| [Twilio](/docs/integrations/tools/twilio) | This notebook goes over how to use the Twilio API wrapper to send a m... |
| [Upstage](/docs/integrations/tools/upstage_groundedness_check) | This notebook covers how to get started with Upstage groundedness che... |
| [Wikidata](/docs/integrations/tools/wikidata) | Wikidata is a free and open knowledge base that can be read and edite... |
| [Wikipedia](/docs/integrations/tools/wikipedia) | Wikipedia is a multilingual free online encyclopedia written and main... |
| [Wolfram Alpha](/docs/integrations/tools/wolfram_alpha) | This notebook goes over how to use the wolfram alpha component. |
| [Yahoo Finance News](/docs/integrations/tools/yahoo_finance_news) | This notebook goes over how to use the yahoofinancenews tool with an ... |
| [You.com Search](/docs/integrations/tools/you) | The you.com API is a suite of tools designed to help developers groun... |
| [YouTube](/docs/integrations/tools/youtube) | YouTube Search package searches YouTube videos avoiding using their h... |
| [Zapier Natural Language Actions](/docs/integrations/tools/zapier) | Deprecated This API will be sunset on 2023-11-17//nla.zapier.com/star... |
| [ZenGuard AI](/docs/integrations/tools/zenguard) | This tool lets you quickly set up ZenGuard AI in your Langchain-power... |

* * *

#### Was this page helpful?

- [Search](#search)
- [Code Interpreter](#code-interpreter)
- [Productivity](#productivity)
- [Web Browsing](#web-browsing)
- [Database](#database)
- [All tools](#all-tools)