# experimentation

Use marinade finance as a test example (liquid staking directory)

Use this:
```
find . -type f -name "*.rs"

```

 + grab all rust files
 + Use regex to extract all functions from the entire codebase
 + grok each one for semantically similar vulnerable bits of code in the txtAI embeddings
 + Rank them, take ones greater than a certain risk
 + RAG those into the the prompt, say 2-3
 + Ask ChatGPT if it has found anything
 + Return results
 + Perhaps even add in bounties `https://immunefi.com/bounty/marinade/`


