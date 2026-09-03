import os

filepath = os.path.join(os.path.dirname(__file__), 'chatbot', 'chat_service.py')

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = 'RESPONSE FORMAT (CRITICAL - MUST FOLLOW):'
end_marker = 'Core behavior:'
start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print(f'ERROR: start={start_idx}, end={end_idx}')
else:
    bullet = chr(0x2022)
    new_section = f"""RESPONSE FORMAT (CRITICAL - MUST FOLLOW):
Format responses with clear visual structure:

**Heading**
Text content with proper spacing.

**Another Heading**
{bullet} Bullet point 1
{bullet} Bullet point 2

FORMATTING RULES:
- Use **bold** for headings (double asterisks)
- Add blank line after each heading before text starts
- Use bullet points ({bullet}) for lists
- Add spacing between sections (blank lines)
- Never write text immediately after a heading without a line break

RESPONSE LENGTH - ADAPT TO QUESTION:
- Simple greeting or short question: 20-40 words
- Basic "how to" or "what is" question: 40-80 words with 2-3 bullet points
- Complex question asking for details, comparisons, or multiple topics: 100-200 words with multiple sections
- If user asks for "detailed explanation", "tell me more", "describe", or similar: give comprehensive response with multiple headings and detailed bullet points

Match response depth to question complexity. Don't give short answers to complex questions.

"""

    content = content[:start_idx] + new_section + content[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS')
