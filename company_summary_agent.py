from docx import Document
import re
from langchain_mistralai.chat_models import ChatMistralAI
from langchain.prompts import ChatPromptTemplate
import textwrap
import os

# === 1. Clean .docx text ===
def clean_docx_text(docx_path):
    doc = Document(docx_path)
    raw_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    clean_text = re.sub(r"!\[.*?\]\(.*?\)", "", raw_text)
    clean_text = re.sub(r"\[.*?\]\(.*?\)", "", clean_text)
    clean_text = re.sub(r"properties\.\w+", "", clean_text)
    clean_text = re.sub(r"\s{2,}", " ", clean_text)
    clean_text = re.sub(r"\\+", "", clean_text)
    return clean_text.strip()

text = clean_docx_text("Website_Crawl_Report.docx")

# === 2. Chunk safely ===
def chunk_text(text, max_chars=10000):
    return textwrap.wrap(text, max_chars)

chunks = chunk_text(text)

# === 3. Setup Mistral model ===
os.environ["MISTRAL_API_KEY"] = "Ta9MbiU93vp6LGiJXVG4A4YC5gXdmutO"
llm = ChatMistralAI(model="mistral-small", temperature=0.2)

# === 4. Prompt templates ===

chunk_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are part of a multi-stage summarization process. Your job is to summarize the following chunk as PART OF A LARGER REPORT.\n"
     "Do not repeat general info. Use consistent tone and format. Focus only on what this chunk uniquely contributes."),
    ("human", "{chunk}")
])

combine_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a business analyst. Combine these partial summaries into one clear, complete, non-repetitive company summary. "
     "Structure the output under these headings:\n"
     "1. Company Name\n2. Industry\n3. Mission\n4. Products & Services\n5. Notable Points\n"),
    ("human", "{summaries}")
])

# === 5. Summarize chunks ===
partial_summaries = []
for i, chunk in enumerate(chunks):
    print(f"⏳ Summarizing chunk {i+1}/{len(chunks)}...")
    response = llm.invoke(chunk_prompt.format_messages(chunk=chunk))
    partial_summaries.append(response.content)

# === 6. Combine summaries into one cohesive output ===
combined_input = "\n\n".join(partial_summaries)
final_response = llm.invoke(combine_prompt.format_messages(summaries=combined_input))
final_summary = final_response.content

# === 7. Save result ===
with open("company_summary.txt", "w", encoding="utf-8") as f:
    f.write(final_summary)

print("\n✅ Final Company Summary:\n")
print(final_summary)
