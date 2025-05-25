def summarize_product(num1, num2, product, client=None):
    """Use OpenAI API to summarize the product of two numbers."""
    prompt = (
        "Write a short sentence summarizing the product of "
        f"{num1} and {num2}, which equals {product}."
    )

    if client is None:
        return f"(No AI) The product of {num1} and {num2} is {product}."

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return f"(Error) The product of {num1} and {num2} is {product}."
