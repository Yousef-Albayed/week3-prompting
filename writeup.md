# Week 3 — Prompting Techniques Write-Up

## Technique 1: K-Shot Prompting (`k_shot_prompting.py`)

### Final Prompt
```text
You are a customer support ticket classification system.
Classify the customer's message into exactly one of the following categories:
- billing
- shipping
- returns
- technical
- other

Respond with ONLY the category label in lowercase. Do not include any punctuation, quotes, or additional text.

Examples:
Customer: "I noticed an incorrect charge on my bank statement from you."
billing

Customer: "When will order 1234 be delivered?"
shipping

Customer: "I would like to return these boots and get my money back."
returns

Customer: "The website shows an error page when I click proceed to checkout."
technical

Customer: "Do you have any open job positions at your headquarters?"
other
```

### Sample Input & Output
- **Input:** `"My card was charged twice for order 4412."`
- **Output:** `billing`

### What I Learned
Providing concrete few-shot input/output examples strictly constrained the model's output distribution, forcing exact single-token category labels without conversational filler or punctuation.

---

## Technique 2: Chain-of-Thought (`chain_of_thought.py`)

### Final Prompt
```text
You are an expert customer service agent assessing refund eligibility according to the store's policy.
Think step-by-step and show your reasoning:
1. Check the date of purchase: is it within 30 days?
2. Check the condition of the item: is it unused and in original condition?
3. Check if the item is final sale: final-sale items cannot be refunded.

After your reasoning, your very last line MUST be formatted exactly as:
DECISION: YES
or
DECISION: NO

Do not add anything after the DECISION line.
```

### Sample Input & Output
- **Input:** `"Bought 5 days ago but it was a final-sale item."`
- **Output:**
  ```text
  1. Date check: Purchased 5 days ago, which is well within the 30-day return window.
  2. Condition check: Condition is not explicitly specified, but does not override final-sale terms.
  3. Final-sale check: The item is explicitly designated as final-sale, and policy states final-sale items are never refundable.
  DECISION: NO
  ```

### What I Learned
Prompting the model to trace explicit reasoning steps prevents premature conclusion jumps on multi-condition policies while maintaining parseable automated grading via a designated final-line delimiter.

---

## Technique 3: Tool Calling (`tool_calling.py`)

### Final Tool Schema & System Prompt
- **Function Description:** `"Retrieves the current status and delivery details for a customer order by its order ID."`
- **Parameter Description:** `"The unique order ID to look up (e.g., '4412')."`
- **System Prompt:**
  ```text
  You are a customer service assistant. When a user asks about an order or asks to check on an order, you must call the get_order_status tool using the extracted order ID before providing a reply.
  ```

### Sample Input & Output
- **Input:** `"Hi, can you check on order 4412 for me?"`
- **Tool Call Output:** `get_order_status(order_id='4412')`
- **Execution Result:** `shipped, arriving Friday`

### What I Learned
Clear function and parameter descriptions enable the LLM to reliably bridge natural language intent to deterministic external API invocations by isolating arguments into structured JSON.

---

## Technique 4: RAG (`rag.py`)

### Final Retriever & System Prompt
- **Retriever:** Tokenizes queries without stopwords, performing root-stem prefix matching against lines in `data/help_center.txt`.
- **System Prompt:**
  ```text
  You are a helpful customer support assistant. Answer the user's question using ONLY the facts provided in the Context.
  If the answer is not contained in the Context, you MUST explicitly state that you do not know (e.g., "I do not know"). Never hallucinate or assume facts not present in the Context.
  ```

### Sample Input & Output
- **Input:** `"How long do I have to return an item?"`
  - **Output:** `"you have 30 days from the delivery date to return an item."`
- **Input:** `"What's your CEO's home address?"`
  - **Output:** `"i do not know."`

### What I Learned
Grounding generation with retrieved factual snippets and explicit refusal instructions eliminates hallucination when queries fall outside the provided knowledge base.

---

## Closing Reflection

Across all four techniques, large language models prove exceptionally adept at structured tasks because their pre-training encodes strong pattern recognition, semantic parsing, and linguistic reasoning capabilities. When given clear instructions, few-shot demonstrations, or schemas, they can translate ambiguous human queries into uniform categories, multi-step deductions, or API arguments. However, they lack inherent factual ground truth, live environment access, and deterministic guardrails on their own. They need scaffolding—such as few-shot constraints for formatting, chain-of-thought protocols for logical verification, tool definitions for environment interaction, and retrieval pipelines for grounded knowledge—to anchor their generative capabilities into robust, reliable software systems.

