import json
import os

import dotenv
from txtai.embeddings import Embeddings
from build_embeddings import get_vulnerabilities
import requests

dotenv.load_dotenv()


class ChatRequest:
    def __init__(self, model, messages):
        self.model = model
        self.messages = messages

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def search_embeddings(query):
    embeddings = Embeddings()
    embeddings.load("vulnerabilities-index")
    results = embeddings.search(query, limit=1)  # limit=1 to get the most relevant result

    data = get_vulnerabilities()

    if results:
        most_relevant_id, score = results[0]
        print(f"Most Relevant ID: {most_relevant_id}, Score: {score}")

        most_relevant_data = next(item for item in data if item['id'] == most_relevant_id)

        print(f"RAG score: {score}")

        rag_string = f"""Description: {most_relevant_data['description']}
        
Example insecure code which may help: 
```rs
{most_relevant_data['insecure_code']}
```

Example secure code which fixes the above (if needed):
```rs
{most_relevant_data['secure_code']}
```"""
        return rag_string
    else:
        raise ValueError('no rag data was retrieved')


def analyze_vulnerability_with_gpt(api_key, file_content):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    rag = search_embeddings(file_content)

    prompt = f"""
[no prose]
You need to answer at all time using a JSON object of this format:

Array<{{ severity: "HIGH"|"MEDIUM"|"LOW"; message: string; errorCode: string; filename: string; lines: Array<number> }}>;

If you find no errors, you should return an empty array.

The filename key should contain the name of the module.

You are an Solana smart contract auditor. You are an expert at finding vulnerabilities that can be exploited by bad people.

The code to audit
```rs
'{file_content}'
```

The below was found in the vector database and may provide a useful strategy to find issues in the code above

'{rag}

NEVER EVER EVER RETURN ANYTHING ELSE THAN JSON. DON'T RETURN MARKDOWN
"""

    print(prompt)

    chat_request = ChatRequest(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    response = requests.post(url, headers=headers, data=chat_request.toJSON())

    if response.ok:
        response_json = response.json()
        response_content = response_json["choices"][0]["message"]["content"]
        print(response_content)


if __name__ == "__main__":
    api_key = os.getenv("CHATGPT_API_KEY")
    file_content = """
    use anchor_lang::prelude::*;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");
#[program]
pub mod signer_authorization_insecure {
    use super::*;

    pub fn log_message(ctx: Context<LogMessage>) -> ProgramResult {
        msg!("GM {}", ctx.accounts.authority.key().to_string());
        Ok(())
    }
}

#[derive(Accounts)]
pub struct LogMessage<'info> {
    authority: AccountInfo<'info>,
}
    """
    print(analyze_vulnerability_with_gpt(api_key, file_content))
