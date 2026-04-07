# CrowdWisdomTrading Prediction Market Research Agents

This project is a backend Python solution for the CrowdWisdomTrading intern assignment. It implements an agent pipeline that:

1. Finds consistent traders in Polymarket
2. Finds consistent traders in Kalshi
3. Maps traders into niches such as politics, sports, and weather
4. Enriches event research using an APIFY-compatible adapter
5. Chats with the collected data to explain which traders are worth copying
6. Runs a closed learning loop that updates trader scores from feedback and outcomes

The code is intentionally runnable without external credentials by using bundled sample data. When `OPENROUTER_API_KEY` and `APIFY_TOKEN` are available, the adapters can call live services instead of the mock mode.

## How to run

From the `cwt_prediction_agents` folder:

```powershell
$env:PYTHONPATH='src'
py -3 -m prediction_agents.main
```

Run tests:

```powershell
$env:PYTHONPATH='src'
py -3 -m unittest discover -s tests -v
```

## Environment variables

- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL` default: `openai/gpt-4o-mini`
- `APIFY_TOKEN`
- `APIFY_ACTOR_ID` default: `apify/website-content-crawler`

## Notes

- The PDF requested Hermes Agent or MiroShark. This implementation uses a Hermes-style multi-agent architecture with clear tool/agent boundaries, storage, reasoning, and a closed learning loop.
- OpenRouter is integrated in the chat agent.
- APIFY is integrated in the event research agent.
- Sample input/output is included via bundled data and the example output file.
