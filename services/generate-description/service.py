from schemas import GenerateDescriptionResponse


async def generate_description(text: str, prompt: str) -> GenerateDescriptionResponse:
    # Mock response
    return GenerateDescriptionResponse(
        text=text,
        prompt=prompt,
    )
